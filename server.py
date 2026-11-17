from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from main import load_matching_persisted_run, run_pipeline
from agents.brsr_extractor import extract_brsr_pdf, persist_extracted_brsr_record
import seed_enterprise_db

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_FILE = FRONTEND_DIR / "index.html"
STYLES_FILE = FRONTEND_DIR / "styles.css"
APP_JS_FILE = FRONTEND_DIR / "app.js"
PLOTLY_JS_FILE = FRONTEND_DIR / "plotly.min.js"

MAX_CSV_BYTES = 64 * 1024 * 1024
MAX_BRSR_PDF_BYTES = 64 * 1024 * 1024

ORGANIZATIONS = [
    "ITC Limited",
    "Reliance Industries Limited",
    "NTPC Limited",
    "Tata Steel Limited",
    "HCL Technologies Limited",
    "Infosys Limited",
    "Tata Consultancy Services Limited",
    "Wipro Limited",
    "Apex Manufacturing Pvt Ltd",
    "GreenGrid Logistics Corp",
]

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

app = FastAPI(title="CarbonTrace", version="5.0.0", description="Indian Corporate Regulatory Carbon Intelligence Platform")

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


class RunRequest(BaseModel):
    org_name: str = Field(min_length=1, max_length=120)
    country: str = Field(default="India", min_length=1, max_length=80)
    start_year: int = Field(default=2000, ge=1990, le=2030)
    end_year: int = Field(default=2025, ge=1990, le=2030)
    cin_number: str | None = Field(default=None, max_length=35)


def _dashboard_payload(state: dict[str, Any]) -> dict[str, Any]:
    metrics = state.get("computed_metrics", {})
    ml_metrics = state.get("ml_evaluation_metrics", {})
    scopes = state.get("scope_breakdown", {})
    brsr_data = state.get("brsr_reported_data", {})
    dq = state.get("data_quality_report", {})

    cin = metrics.get("cin_number") or brsr_data.get("cin_number")
    company_name = brsr_data.get("company_name") or metrics.get("company_name") or metrics.get("org_name", state.get("org_name", "Unknown organization"))

    # Look up registry metadata for company_name if available
    reg_entry = next((item for item in seed_enterprise_db.CORPORATE_CIN_REGISTRY if item["org_name"].lower() == str(company_name).lower()), {})
    if not cin and reg_entry:
        cin = reg_entry.get("cin_number")

    s1_val = metrics.get("reported_scope_1_tco2e") or brsr_data.get("reported_scope_1_tco2e") or reg_entry.get("reported_scope_1_tco2e")
    s2_val = metrics.get("reported_scope_2_tco2e") or brsr_data.get("reported_scope_2_tco2e") or reg_entry.get("reported_scope_2_tco2e")
    s3_val = metrics.get("reported_scope_3_tco2e") or brsr_data.get("reported_scope_3_tco2e") or reg_entry.get("reported_scope_3_tco2e")

    # Calculate renewable percentage dynamically if energy breakdown exists
    en_total = metrics.get("energy_consumption_value") or brsr_data.get("energy_consumption_value") or reg_entry.get("energy_consumption_value") or 0.0
    en_renew = brsr_data.get("renewable_energy_tj") or 0.0
    renew_pct = round((en_renew / en_total) * 100.0, 1) if en_total > 0 and en_renew > 0 else None

    # Determine provenance dynamically
    brsr_prov = brsr_data.get("data_provenance") or metrics.get("brsr_data_provenance") or (
        "VERIFIED_BRSR_EXTRACTED" if brsr_data.get("reported_scope_1_tco2e") is not None else "SYNTHETIC_DEMO"
    )
    raw_prov = brsr_prov if (brsr_data.get("data_provenance") == "VERIFIED_BRSR_EXTRACTED" or metrics.get("brsr_data_provenance") == "VERIFIED_BRSR_EXTRACTED") else (metrics.get("data_provenance") or "SYNTHETIC_DEMO")

    scopes_list = [
        {"label": label, "tco2e": value}
        for label, value in scopes.items()
    ] if scopes else []
    if not scopes_list:
        if s1_val is not None:
            scopes_list.append({"label": "Scope 1: Stationary & Fleet Combustion", "tco2e": s1_val})
        if s2_val is not None:
            scopes_list.append({"label": "Scope 2: Location-Based Electricity", "tco2e": s2_val})
        if s3_val is not None:
            scopes_list.append({"label": "Scope 3: Value Chain & Freight", "tco2e": s3_val})

    return {
        "ok": state.get("ingestion_status") == "SUCCESS",
        "organization": company_name,
        "country": metrics.get("benchmark_country", state.get("target_entity", "India")),
        "period": {
            "start_year": metrics.get("start_year", state.get("start_year")),
            "end_year": metrics.get("end_year", state.get("end_year")),
        },
        "provenance": raw_prov,
        "corporate": {
            "cin_number": cin,
            "company_name": company_name,
            "bse_code": metrics.get("bse_code") or brsr_data.get("bse_code") or reg_entry.get("bse_code"),
            "nse_symbol": metrics.get("nse_symbol") or brsr_data.get("nse_symbol") or reg_entry.get("nse_symbol"),
            "filing_section": metrics.get("filing_section") or brsr_data.get("filing_section") or reg_entry.get("filing_section") or "Section C: Principle 6",
            "financial_year": metrics.get("financial_year") or brsr_data.get("financial_year"),
            "previous_financial_year": brsr_data.get("previous_financial_year"),
            "assurance_provider": brsr_data.get("assurance_provider") or reg_entry.get("assurance_provider"),
            "document_format": metrics.get("document_format") or brsr_data.get("document_format", "NATIVE_DIGITAL_TEXT"),
            "pages_scanned": metrics.get("pages_scanned") or brsr_data.get("pages_scanned", 1),
            "extraction_engine": metrics.get("extraction_engine") or brsr_data.get("extraction_engine", "pdfplumber+pypdf"),
            "data_provenance": brsr_prov,
            "brsr_provenance": brsr_prov,
            "brsr_source": metrics.get("brsr_source") or brsr_data.get("source"),
            "reported_scope_1_tco2e": s1_val,
            "reported_scope_1_ktco2e": round(s1_val / 1000.0, 3) if s1_val is not None else None,
            "reported_scope_2_tco2e": s2_val,
            "reported_scope_2_ktco2e": round(s2_val / 1000.0, 3) if s2_val is not None else None,
            "scope_2_market_tco2e": brsr_data.get("scope_2_market_tco2e"),
            "scope_2_location_tco2e": brsr_data.get("scope_2_location_tco2e") or s2_val,
            "reported_scope_3_tco2e": s3_val,
            "reported_scope_3_ktco2e": round(s3_val / 1000.0, 3) if s3_val is not None else None,
            "total_extracted_footprint_tco2e": metrics.get("total_extracted_footprint_tco2e") or brsr_data.get("total_extracted_footprint_tco2e") or (
                ((s1_val or 0.0) + (s2_val or 0.0) + (s3_val or 0.0)) if (s1_val is not None or s2_val is not None or s3_val is not None) else None
            ),
            "scope_1_reconciliation_variance_tco2e": metrics.get("scope_1_reconciliation_variance_tco2e"),
            "scope_2_reconciliation_variance_tco2e": metrics.get("scope_2_reconciliation_variance_tco2e"),
            "scope_3_reconciliation_variance_tco2e": metrics.get("scope_3_reconciliation_variance_tco2e"),
            "energy_consumption_value": en_total if en_total > 0 else None,
            "energy_consumption_unit": metrics.get("energy_consumption_unit") or brsr_data.get("energy_consumption_unit"),
            "energy_consumption_gj": metrics.get("energy_consumption_gj") or brsr_data.get("energy_consumption_gj"),
            "energy_consumption_kwh": metrics.get("energy_consumption_kwh") or brsr_data.get("energy_consumption_kwh"),
            "renewable_energy_tj": brsr_data.get("renewable_energy_tj"),
            "non_renewable_energy_tj": brsr_data.get("non_renewable_energy_tj"),
            "renewable_electricity_tj": brsr_data.get("renewable_electricity_tj"),
            "renewable_fuel_tj": brsr_data.get("renewable_fuel_tj"),
            "non_renewable_electricity_tj": brsr_data.get("non_renewable_electricity_tj"),
            "non_renewable_fuel_tj": brsr_data.get("non_renewable_fuel_tj"),
            "renewable_share_pct": renew_pct,
            "energy_intensity_per_turnover": brsr_data.get("energy_intensity_per_turnover_gj_per_crore"),
            "ghg_emission_intensity_per_turnover": brsr_data.get("ghg_emission_intensity_tco2e_per_crore"),
            "disclosures_matrix": metrics.get("disclosures_matrix") or brsr_data.get("disclosures_matrix", []),
            "previous_fy_data": brsr_data.get("previous_fy_data") or {},
        },
        "regulatory_stepper": {
            "step1_mca": True,
            "step2_cin": bool(cin),
            "step3_filing": bool(cin or s1_val is not None),
            "step4_principle6": bool(s1_val is not None or en_total > 0),
        },
        "last_run": state.get("_last_run_timestamp_utc", "Live Synced"),
        "critic_approved": state.get("critic_approved", True),
        "critic_completeness": state.get("faithfulness_score", 100.0),
        "metrics": {
            "end_org_tco2e": metrics.get("end_org_tco2e"),
            "start_org_tco2e": metrics.get("start_org_tco2e"),
            "org_net_change_pct": metrics.get("org_net_change_pct"),
            "org_cagr_pct": metrics.get("org_cagr_pct"),
            "owid_national_end_co2_mt": metrics.get("owid_national_end_co2_mt"),
            "owid_national_net_change_pct": metrics.get("owid_national_net_change_pct"),
            "cagr_decoupling_alpha_pct": metrics.get("cagr_decoupling_alpha_pct"),
            "ridge_rmse_tco2e": ml_metrics.get("rmse_tco2e"),
            "naive_rmse_tco2e": ml_metrics.get("baseline_naive_rmse_tco2e"),
            "rmse_skill_over_naive_pct": ml_metrics.get("rmse_skill_over_naive_pct"),
            "worse_than_baseline": ml_metrics.get("worse_than_baseline", False),
            "agreement_f1": ml_metrics.get("consensus_f1_score"),
            "silhouette_score": ml_metrics.get("silhouette_score"),
            "walk_forward_folds": ml_metrics.get("walk_forward_folds"),
            "forecast_horizon": ml_metrics.get("forecast_horizon_label", "2026–2032"),
            "forecast_status": ml_metrics.get("status", "COMPLETED"),
        },
        "scopes": scopes_list,
        "history": state.get("annual_emissions_records", []),
        "forecast": state.get("forecast_records", []),
        "anomalies": state.get("anomalies_detected", []),
        "report": state.get("draft_report", ""),
        "data_quality": dq,
        "agent_logs": state.get("agent_logs", []),
    }


def _run_and_encode(
    request: RunRequest,
    data_source_path: str | None = None,
    brsr_pdf_path: str | None = None,
) -> dict[str, Any]:
    if request.start_year > request.end_year:
        raise HTTPException(status_code=422, detail="Start year must not be after end year.")
    state = run_pipeline(
        entity=request.country,
        start_year=request.start_year,
        end_year=request.end_year,
        org_name=request.org_name,
        data_source_path=data_source_path,
        cin_number=request.cin_number,
        brsr_pdf_path=brsr_pdf_path,
    )
    return _dashboard_payload(state)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    if not FRONTEND_FILE.exists():
        raise HTTPException(status_code=404, detail="Frontend file not found.")
    return FileResponse(FRONTEND_FILE, media_type="text/html")


@app.get("/styles.css", include_in_schema=False)
def get_styles() -> FileResponse:
    if STYLES_FILE.exists():
        return FileResponse(STYLES_FILE, media_type="text/css")
    return FileResponse(FRONTEND_FILE, media_type="text/html")


@app.get("/app.js", include_in_schema=False)
def get_app_js() -> FileResponse:
    if APP_JS_FILE.exists():
        return FileResponse(APP_JS_FILE, media_type="application/javascript")
    return FileResponse(FRONTEND_FILE, media_type="text/html")


@app.get("/plotly.min.js", include_in_schema=False)
def get_plotly_js() -> FileResponse:
    if PLOTLY_JS_FILE.exists():
        return FileResponse(PLOTLY_JS_FILE, media_type="application/javascript")
    return FileResponse(FRONTEND_FILE, media_type="text/html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "CarbonTrace", "version": "5.0.0"}


@app.get("/api/companies")
@app.get("/api/organizations")
def companies() -> dict[str, Any]:
    import sqlite3
    seed_enterprise_db.initialize_enterprise_data_store()
    conn = sqlite3.connect(seed_enterprise_db.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT org_id FROM enterprise_activity_logs")
    act_corps = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT org_name FROM corporate_cin_registry")
    reg_corps = [r[0] for r in cur.fetchall()]
    conn.close()

    all_orgs = list(dict.fromkeys(ORGANIZATIONS + act_corps + reg_corps))
    return {
        "companies": all_orgs,
        "organizations": all_orgs,
        "countries": COUNTRIES,
        "registry": seed_enterprise_db.CORPORATE_CIN_REGISTRY,
    }


@app.get("/api/run")
def latest_run(
    org_name: str = "ITC Limited",
    country: str = "India",
    start_year: int = 2000,
    end_year: int = 2025,
    cin_number: str | None = None,
) -> dict[str, Any]:
    request = RunRequest(
        org_name=org_name,
        country=country,
        start_year=start_year,
        end_year=end_year,
        cin_number=cin_number,
    )
    state = load_matching_persisted_run(org_name, country, start_year, end_year)
    if state is None:
        return _run_and_encode(request)
    return _dashboard_payload(state)


@app.post("/api/run")
def run(request: RunRequest) -> dict[str, Any]:
    return _run_and_encode(request)


@app.post("/api/upload-csv")
@app.post("/api/run-csv")
async def run_csv(request: Request) -> dict[str, Any]:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="CSV must be 64 MB or smaller.")

    org_name = request.query_params.get("org_name", "Apex Manufacturing Pvt Ltd")
    country = request.query_params.get("country", "India")
    start_year = int(request.query_params.get("start_year", "2000"))
    end_year = int(request.query_params.get("end_year", "2023"))
    cin_number = request.query_params.get("cin_number")
    run_request = RunRequest(
        org_name=org_name,
        country=country,
        start_year=start_year,
        end_year=end_year,
        cin_number=cin_number,
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


@app.post("/api/upload-brsr-pdf")
@app.post("/api/run-brsr")
async def run_brsr(request: Request) -> dict[str, Any]:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BRSR_PDF_BYTES:
        raise HTTPException(status_code=413, detail="BRSR PDF must be 64 MB or smaller.")

    org_name = request.query_params.get("org_name", "")
    country = request.query_params.get("country", "India")
    start_year = int(request.query_params.get("start_year", "2000"))
    end_year = int(request.query_params.get("end_year", "2025"))
    cin_number = request.query_params.get("cin_number")
    filename = request.headers.get("x-filename", "") or request.query_params.get("filename", "")

    pdf_bytes = await request.body()
    if len(pdf_bytes) > MAX_BRSR_PDF_BYTES:
        raise HTTPException(status_code=413, detail="BRSR PDF must be 64 MB or smaller.")
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="Uploaded file is not a valid PDF.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        extracted = {}
        try:
            extracted = extract_brsr_pdf(temp_path, filename=filename)
            # When a PDF is uploaded, the extracted company name MUST override the UI's previous selection
            if extracted.get("company_name"):
                org_name = extracted["company_name"]
            if extracted.get("cin_number"):
                cin_number = extracted["cin_number"]
            persist_extracted_brsr_record(extracted)
        except Exception as exc:
            print(f"[Upload BRSR] Extraction warning: {exc}")

        run_request = RunRequest(
            org_name=org_name or "ITC Limited",
            country=country,
            start_year=start_year,
            end_year=end_year,
            cin_number=cin_number,
        )
        dashboard = await run_in_threadpool(_run_and_encode, run_request, None, temp_path)
        dashboard["extracted_brsr"] = extracted
        return dashboard
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@app.post("/api/extract-brsr")
async def extract_brsr_standalone(request: Request) -> dict[str, Any]:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BRSR_PDF_BYTES:
        raise HTTPException(status_code=413, detail="BRSR PDF must be 64 MB or smaller.")

    pdf_bytes = await request.body()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="Uploaded file is not a valid PDF.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name
        return await run_in_threadpool(extract_brsr_pdf, temp_path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)