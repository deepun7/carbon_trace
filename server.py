from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from main import load_matching_persisted_run, run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_FILE = PROJECT_ROOT / "frontend" / "index.html"
MAX_CSV_BYTES = 64 * 1024 * 1024
ORGANIZATIONS = ["Apex Manufacturing Pvt Ltd", "GreenGrid Logistics Corp"]
COUNTRIES = [
    "India",
    "United States",
    "China",
    "European Union (27)",
    "United Kingdom",
    "Germany",
    "Japan",
    "World",
]

app = FastAPI(title="CarbonTrace", version="2.0.0")


class RunRequest(BaseModel):
    org_name: str = Field(min_length=1, max_length=120)
    country: str = Field(default="India", min_length=1, max_length=80)
    start_year: int = Field(default=2000, ge=2000, le=2023)
    end_year: int = Field(default=2023, ge=2000, le=2023)


def _dashboard_payload(state: dict[str, Any]) -> dict[str, Any]:
    metrics = state.get("computed_metrics", {})
    ml_metrics = state.get("ml_evaluation_metrics", {})
    scopes = state.get("scope_breakdown", {})
    return {
        "ok": state.get("ingestion_status") == "SUCCESS",
        "organization": metrics.get("org_name", state.get("org_name", "Unknown organization")),
        "country": metrics.get("benchmark_country", state.get("target_entity", "Unknown")),
        "period": {
            "start_year": metrics.get("start_year", state.get("start_year")),
            "end_year": metrics.get("end_year", state.get("end_year")),
        },
        "provenance": metrics.get("data_provenance", "SIMULATED_DEMO"),
        "last_run": state.get("_last_run_timestamp_utc", "Not available"),
        "critic_approved": state.get("critic_approved", False),
        "critic_completeness": state.get("faithfulness_score", 0.0),
        "metrics": {
            "end_org_tco2e": metrics.get("end_org_tco2e"),
            "org_net_change_pct": metrics.get("org_net_change_pct"),
            "owid_national_end_co2_mt": metrics.get("owid_national_end_co2_mt"),
            "ridge_rmse_tco2e": ml_metrics.get("rmse_tco2e"),
            "naive_rmse_tco2e": ml_metrics.get("baseline_naive_rmse_tco2e"),
            "rmse_skill_over_naive_pct": ml_metrics.get("rmse_skill_over_naive_pct"),
            "worse_than_baseline": ml_metrics.get("worse_than_baseline", False),
            "agreement_f1": ml_metrics.get("consensus_f1_score"),
            "walk_forward_folds": ml_metrics.get("walk_forward_folds"),
            "forecast_horizon": ml_metrics.get("forecast_horizon_label", "N/A"),
            "forecast_status": ml_metrics.get("status", "N/A"),
        },
        "scopes": [
            {"label": label, "tco2e": value}
            for label, value in scopes.items()
        ],
        "history": state.get("annual_emissions_records", []),
        "forecast": state.get("forecast_records", []),
        "anomalies": state.get("anomalies_detected", []),
        "report": state.get("draft_report", ""),
        "data_quality": state.get("data_quality_report", {}),
        "agent_logs": state.get("agent_logs", []),
    }


def _run_and_encode(request: RunRequest, data_source_path: str | None = None) -> dict[str, Any]:
    if request.start_year > request.end_year:
        raise HTTPException(status_code=422, detail="Start year must not be after end year.")
    state = run_pipeline(
        entity=request.country,
        start_year=request.start_year,
        end_year=request.end_year,
        org_name=request.org_name,
        data_source_path=data_source_path,
    )
    return _dashboard_payload(state)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_FILE, media_type="text/html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "CarbonTrace"}


@app.get("/api/organizations")
def organizations() -> dict[str, list[str]]:
    return {"organizations": ORGANIZATIONS, "countries": COUNTRIES}


@app.get("/api/run")
def latest_run(
    org_name: str = "Apex Manufacturing Pvt Ltd",
    country: str = "India",
    start_year: int = 2000,
    end_year: int = 2023,
) -> dict[str, Any]:
    request = RunRequest(
        org_name=org_name,
        country=country,
        start_year=start_year,
        end_year=end_year,
    )
    state = load_matching_persisted_run(org_name, country, start_year, end_year)
    if state is None:
        return _run_and_encode(request)
    return _dashboard_payload(state)


@app.post("/api/run")
def run(request: RunRequest) -> dict[str, Any]:
    return _run_and_encode(request)


@app.post("/api/run-csv")
async def run_csv(request: Request) -> dict[str, Any]:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="CSV must be 64 MB or smaller.")

    org_name = request.query_params.get("org_name", "Apex Manufacturing Pvt Ltd")
    country = request.query_params.get("country", "India")
    start_year = int(request.query_params.get("start_year", "2000"))
    end_year = int(request.query_params.get("end_year", "2023"))
    run_request = RunRequest(
        org_name=org_name,
        country=country,
        start_year=start_year,
        end_year=end_year,
    )
    csv_bytes = await request.body()
    if len(csv_bytes) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="CSV must be 64 MB or smaller.")
    if not csv_bytes.strip():
        raise HTTPException(status_code=422, detail="Uploaded CSV is empty.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_file.write(csv_bytes)
            temp_path = temp_file.name
        return await run_in_threadpool(_run_and_encode, run_request, temp_path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)