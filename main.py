import os
from langgraph.graph import StateGraph, END
from state import CarbonAgentState
from agents.ingestion import ingestion_agent
from agents.calculation import calculation_agent
from agents.ml_engine import ml_engine_agent
from agents.reporting import reporting_agent
from agents.critic import critic_agent

def route_after_ingestion(state: CarbonAgentState) -> str:
    if state.get("ingestion_status") == "SUCCESS" and len(state.get("raw_records", [])) > 0:
        return "calculate"
    return "end"

def route_after_critic(state: CarbonAgentState) -> str:
    if state.get("critic_approved", False):
        return "end"
    return "regenerate"

def build_carbontrace_graph():
    workflow = StateGraph(CarbonAgentState)

    # Register All 5 Autonomous Nodes
    workflow.add_node("ingestion_node", ingestion_agent)
    workflow.add_node("calculation_node", calculation_agent)
    workflow.add_node("ml_engine_node", ml_engine_agent)
    workflow.add_node("reporting_node", reporting_agent)
    workflow.add_node("critic_node", critic_agent)

    workflow.set_entry_point("ingestion_node")

    workflow.add_conditional_edges(
        "ingestion_node",
        route_after_ingestion,
        {"calculate": "calculation_node", "end": END}
    )

    workflow.add_edge("calculation_node", "ml_engine_node")
    workflow.add_edge("ml_engine_node", "reporting_node")
    workflow.add_edge("reporting_node", "critic_node")

    workflow.add_conditional_edges(
        "critic_node",
        route_after_critic,
        {"regenerate": "reporting_node", "end": END}
    )

    return workflow.compile()

def run_pipeline(entity: str = "India", start_year: int = 2000, end_year: int = 2023) -> CarbonAgentState:
    app = build_carbontrace_graph()
    initial_state: CarbonAgentState = {
        "target_entity": entity,
        "start_year": start_year,
        "end_year": end_year,
        "raw_records": [],
        "data_quality_notes": [],
        "ingestion_status": "PENDING",
        "computed_metrics": {},
        "anomalies_detected": [],
        "scope_breakdown": {},
        "ml_evaluation_metrics": {},
        "forecast_records": [],
        "draft_report": "",
        "critic_approved": False,
        "critic_feedback": None,
        "faithfulness_score": 0.0,
        "revision_count": 0,
        "agent_logs": []
    }
    return app.invoke(initial_state)

if __name__ == "__main__":
    print("🚀 Running CarbonTrace Autonomous 5-Agent ML Pipeline (CLI Mode)...")
    final_state = run_pipeline("India", 2000, 2023)
    
    print("\n--- AGENT EXECUTION LOGS ---")
    for log in final_state["agent_logs"]:
        print(log)
        
    print("\n--- ML EVALUATION METRICS ---")
    for k, v in final_state["ml_evaluation_metrics"].items():
        print(f"  • {k}: {v}")
        
    if final_state["draft_report"]:
        os.makedirs("reports", exist_ok=True)
        sample_path = os.path.join("reports", "sample_generated_report.md")
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write(final_state["draft_report"])
        print(f"\n✅ Deliverable Saved: '{sample_path}'")