import os
import json
import time
import sqlite3
import argparse
from datetime import datetime, timezone
from langgraph.graph import StateGraph, END
from state import CarbonAgentState
from agents.ingestion import ingestion_agent
from agents.calculation import calculation_agent
from agents.ml_engine import ml_engine_agent
from agents.reporting import reporting_agent
from agents.critic import critic_agent

RUN_LEDGER_DB = os.path.join("data", "pipeline_runs_ledger.db")

def init_run_ledger():
    """Initializes or migrates the run ledger table non-destructively (never drops existing history)."""
    os.makedirs(os.path.dirname(RUN_LEDGER_DB) or ".", exist_ok=True)
    conn = sqlite3.connect(RUN_LEDGER_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS automated_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc TEXT NOT NULL,
            org_name TEXT NOT NULL,
            country TEXT NOT NULL,
            start_year INTEGER NOT NULL DEFAULT 2000,
            end_year INTEGER NOT NULL DEFAULT 2023,
            data_provenance TEXT NOT NULL DEFAULT 'SIMULATED_DEMO',
            status TEXT NOT NULL,
            critic_approved INTEGER NOT NULL,
            faithfulness_score REAL NOT NULL,
            end_org_tco2e REAL,
            state_json TEXT
        )
    """)
    # Non-destructive column migration if upgrading from an older table schema
    cur.execute("PRAGMA table_info(automated_runs)")
    existing_cols = {r[1] for r in cur.fetchall()}
    migrations = [
        ("start_year", "INTEGER NOT NULL DEFAULT 2000"),
        ("end_year", "INTEGER NOT NULL DEFAULT 2023"),
        ("data_provenance", "TEXT NOT NULL DEFAULT 'SIMULATED_DEMO'")
    ]
    for col_name, col_def in migrations:
        if col_name not in existing_cols:
            cur.execute(f"ALTER TABLE automated_runs ADD COLUMN {col_name} {col_def}")
    conn.commit()
    conn.close()

def validate_cli_parameters(start_year: int, end_year: int, interval_minutes: int = 60):
    if start_year > end_year:
        raise ValueError(f"start_year ({start_year}) cannot be greater than end_year ({end_year}).")
    if interval_minutes <= 0:
        raise ValueError(f"interval_minutes ({interval_minutes}) must be a positive integer (> 0).")

def log_run_to_ledger(state: CarbonAgentState, status: str) -> str:
    init_run_ledger()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    provenance = state.get("data_quality_report", {}).get("data_provenance", "SIMULATED_DEMO")
    conn = sqlite3.connect(RUN_LEDGER_DB)
    conn.execute("""
        INSERT INTO automated_runs (
            timestamp_utc, org_name, country, start_year, end_year,
            data_provenance, status, critic_approved, faithfulness_score,
            end_org_tco2e, state_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ts,
        state.get("org_name", ""),
        state.get("target_entity", ""),
        int(state.get("start_year", 2000)),
        int(state.get("end_year", 2023)),
        provenance,
        status,
        1 if state.get("critic_approved") else 0,
        float(state.get("faithfulness_score", 0.0)),
        float(state.get("computed_metrics", {}).get("end_org_tco2e", 0.0)),
        json.dumps(state)
    ))
    conn.commit()
    conn.close()
    return ts

def load_matching_persisted_run(org_name: str, country: str, start_year: int, end_year: int) -> dict | None:
    """Loads the latest completed run ONLY if it matches the requested organization, country, and period."""
    if not os.path.exists(RUN_LEDGER_DB):
        return None
    init_run_ledger()
    conn = sqlite3.connect(RUN_LEDGER_DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp_utc, data_provenance, state_json
        FROM automated_runs
        WHERE status = 'COMPLETED'
          AND LOWER(org_name) = LOWER(?)
          AND LOWER(country) = LOWER(?)
          AND start_year = ?
          AND end_year = ?
        ORDER BY run_id DESC LIMIT 1
    """, (org_name, country, int(start_year), int(end_year)))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    state_obj = json.loads(row[2])
    state_obj["_last_run_timestamp_utc"] = row[0]
    state_obj["_last_run_provenance"] = row[1]
    return state_obj

def load_latest_persisted_run() -> dict | None:
    if not os.path.exists(RUN_LEDGER_DB):
        return None
    init_run_ledger()
    conn = sqlite3.connect(RUN_LEDGER_DB)
    cur = conn.cursor()
    cur.execute("SELECT state_json FROM automated_runs WHERE status = 'COMPLETED' ORDER BY run_id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def route_after_ingestion(state: CarbonAgentState) -> str:
    if state.get("ingestion_status") == "SUCCESS" and len(state.get("org_activity_records", [])) > 0:
        return "calculate"
    return "end"

def route_after_critic(state: CarbonAgentState) -> str:
    if state.get("critic_approved", False):
        return "end"
    if state.get("revision_count", 0) >= 2:
        return "end"
    return "regenerate"

def build_carbontrace_graph():
    workflow = StateGraph(CarbonAgentState)

    workflow.add_node("ingestion_node", ingestion_agent)
    workflow.add_node("calculation_node", calculation_agent)
    workflow.add_node("ml_engine_node", ml_engine_agent)
    workflow.add_node("reporting_node", reporting_agent)
    workflow.add_node("critic_node", critic_agent)

    workflow.set_entry_point("ingestion_node")
    workflow.add_conditional_edges("ingestion_node", route_after_ingestion, {"calculate": "calculation_node", "end": END})
    workflow.add_edge("calculation_node", "ml_engine_node")
    workflow.add_edge("ml_engine_node", "reporting_node")
    workflow.add_edge("reporting_node", "critic_node")
    workflow.add_conditional_edges("critic_node", route_after_critic, {"regenerate": "reporting_node", "end": END})

    return workflow.compile()

def run_pipeline(
    entity: str = "India",
    start_year: int = 2000,
    end_year: int = 2023,
    org_name: str = "Apex Manufacturing Pvt Ltd",
    data_source_path: str = None,
    use_llm_narrative: bool = False,
    save_report_path: str = os.path.join("reports", "sample_generated_report.md")
) -> CarbonAgentState:
    validate_cli_parameters(start_year, end_year, interval_minutes=60)
    app = build_carbontrace_graph()
    initial_state: CarbonAgentState = {
        "org_name": org_name,
        "target_entity": entity,
        "start_year": start_year,
        "end_year": end_year,
        "data_source_path": data_source_path,
        "use_llm_narrative": use_llm_narrative,
        "org_activity_records": [],
        "owid_benchmark_records": [],
        "data_quality_report": {},
        "ingestion_status": "PENDING",
        "computed_metrics": {},
        "scope_breakdown": {},
        "emission_factors_audit": {},
        "annual_emissions_records": [],
        "anomalies_detected": [],
        "ml_evaluation_metrics": {},
        "forecast_records": [],
        "draft_report": "",
        "critic_approved": False,
        "critic_feedback": None,
        "faithfulness_score": 0.0,
        "revision_count": 0,
        "agent_logs": []
    }
    final_state = app.invoke(initial_state)

    if final_state.get("draft_report") and final_state.get("critic_approved"):
        if save_report_path:
            os.makedirs(os.path.dirname(save_report_path) or ".", exist_ok=True)
            with open(save_report_path, "w", encoding="utf-8") as f:
                f.write(final_state["draft_report"])
        ts = log_run_to_ledger(final_state, "COMPLETED")
    else:
        ts = log_run_to_ledger(final_state, "FAILED_VALIDATION")

    final_state["_last_run_timestamp_utc"] = ts
    final_state["_last_run_provenance"] = final_state.get("data_quality_report", {}).get("data_provenance", "SIMULATED_DEMO")
    return final_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CarbonTrace Multi-Agent Prototype Pipeline & Scheduler")
    parser.add_argument("--org", type=str, default="Apex Manufacturing Pvt Ltd", help="Organization Name")
    parser.add_argument("--country", type=str, default="India", help="OWID Benchmark Country")
    parser.add_argument("--start", type=int, default=2000, help="Start Year")
    parser.add_argument("--end", type=int, default=2023, help="End Year")
    parser.add_argument("--csv", type=str, default=None, help="Optional path to external activity CSV")
    parser.add_argument("--use-llm", action="store_true", help="Enable optional LLM executive summary")
    parser.add_argument("--schedule", action="store_true", help="Run periodic scheduler loop with backoff recovery")
    parser.add_argument("--interval-minutes", type=int, default=60, help="Positive schedule interval in minutes (> 0)")
    args = parser.parse_args()

    validate_cli_parameters(args.start, args.end, args.interval_minutes)

    if args.schedule:
        print(f"⏱️ Starting Periodic CarbonTrace Scheduler (Interval: {args.interval_minutes}m)...")
        while True:
            for attempt in range(1, 4):
                try:
                    state = run_pipeline(args.country, args.start, args.end, args.org, args.csv, args.use_llm)
                    print(f"[{state.get('_last_run_timestamp_utc')}] ✅ Run Completed for {args.org} (Critic Approved: {state['critic_approved']})")
                    break
                except Exception as exc:
                    wait_sec = 5 * (2 ** (attempt - 1))
                    print(f"⚠️ Scheduler attempt {attempt}/3 failed: {exc}. Retrying in {wait_sec}s...")
                    time.sleep(wait_sec)
            time.sleep(args.interval_minutes * 60)
    else:
        state = run_pipeline(args.country, args.start, args.end, args.org, args.csv, args.use_llm)
        for log in state["agent_logs"]:
            print(log)
        print(f"\n✅ Deliverable Saved: 'reports/sample_generated_report.md' | Timestamp: {state.get('_last_run_timestamp_utc')}")