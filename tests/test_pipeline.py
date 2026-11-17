import os
import sqlite3
import pandas as pd
import pytest
from fastapi.testclient import TestClient
import seed_enterprise_db
import agents.ingestion as ing_mod
import main as main_mod
import server as server_mod
import agents.brsr_extractor as brsr_mod
from agents.brsr_extractor import extract_brsr_principle_6_text, lookup_cin_metadata, validate_cin
from agents.ingestion import ingestion_agent
from agents.calculation import calculation_agent
from agents.ml_engine import ml_engine_agent
from agents.reporting import reporting_agent
from agents.critic import critic_agent
from main import log_run_to_ledger, load_matching_persisted_run, validate_cli_parameters, init_run_ledger

def _dashboard_state():
    return {
        "org_name": "Apex Manufacturing Pvt Ltd",
        "target_entity": "India",
        "start_year": 2020,
        "end_year": 2023,
        "ingestion_status": "SUCCESS",
        "computed_metrics": {
            "org_name": "Apex Manufacturing Pvt Ltd",
            "benchmark_country": "India",
            "start_year": 2020,
            "end_year": 2023,
            "data_provenance": "SYNTHETIC_DEMO",
            "cin_number": "L17110MH1973PLC019786",
            "bse_code": "500325",
            "nse_symbol": "RELIANCE",
            "filing_section": "Section E: Principle 6",
            "brsr_data_provenance": "VERIFIED_BRSR_EXTRACTED",
            "end_org_tco2e": 4215.63,
            "org_net_change_pct": 8.45,
            "owid_national_end_co2_mt": 3062.756,
        },
        "ml_evaluation_metrics": {
            "rmse_tco2e": 35.2,
            "baseline_naive_rmse_tco2e": 40.1,
            "rmse_skill_over_naive_pct": 12.22,
            "worse_than_baseline": False,
            "consensus_f1_score": 0.75,
            "walk_forward_folds": 2,
            "forecast_horizon_label": "2024–2030",
            "status": "COMPLETED",
        },
        "scope_breakdown": {"Scope 1": 1000.0, "Scope 2": 2000.0, "Scope 3": 1215.63},
        "annual_emissions_records": [{"year": 2023, "total_org_tco2e": 4215.63}],
        "forecast_records": [{"year": 2024, "predicted_org_tco2e": 4300.0}],
        "anomalies_detected": [],
        "draft_report": "CarbonTrace test report",
        "data_quality_report": {"data_provenance": "SYNTHETIC_DEMO"},
        "agent_logs": ["test run"],
        "critic_approved": True,
        "faithfulness_score": 100.0,
        "_last_run_timestamp_utc": "2026-11-04 12:00:00 UTC",
    }

@pytest.fixture(autouse=True)
def isolated_test_environment(tmp_path, monkeypatch):
    """Redirects all SQLite DBs, caches, and factor registries to tmp_path so production data/ is never touched."""
    test_db = str(tmp_path / "test_enterprise_telemetry.db")
    test_ef = str(tmp_path / "test_emission_factors_registry.json")
    test_owid_cache = str(tmp_path / "test_owid_cache.csv")
    test_dropzone = str(tmp_path / "test_dropzone.csv")
    test_ledger = str(tmp_path / "test_pipeline_runs_ledger.db")

    monkeypatch.setattr(seed_enterprise_db, "DB_PATH", test_db)
    monkeypatch.setattr(seed_enterprise_db, "EF_REGISTRY_PATH", test_ef)
    monkeypatch.setattr(ing_mod, "OWID_CACHE_FILE", test_owid_cache)
    monkeypatch.setattr(ing_mod, "EXTERNAL_DROPZONE_CSV", test_dropzone)
    monkeypatch.setattr(main_mod, "RUN_LEDGER_DB", test_ledger)

    # Pre-populate offline OWID cache in tmp_path
    pd.DataFrame(_mock_owid_records(2000, 2023)).to_csv(test_owid_cache, index=False)
    seed_enterprise_db.initialize_enterprise_data_store(force_reset=True)
    yield

def _mock_owid_records(start_year: int = 2000, end_year: int = 2023) -> list[dict]:
    return [
        {
            "country": "India", "year": yr, "iso_code": "IND",
            "population": 1400000000.0, "gdp": 3000000000000.0,
            "co2": 1000.0 + (yr - 2000) * 85.0, "co2_per_capita": 1.9,
            "co2_per_gdp": 0.3, "primary_energy_consumption": 9000.0 + (yr - 2000) * 300.0
        }
        for yr in range(start_year, end_year + 1)
    ]

def test_1_emission_factor_arithmetic_and_multi_facility_aggregation():
    facility_rows = [
        {
            "org_id": "TestOrg", "facility_id": "FAC-1", "year": 2022,
            "stationary_diesel_liters": 1000.0, "natural_gas_m3": 500.0, "fleet_transport_km": 1000.0,
            "purchased_electricity_kwh": 10000.0, "business_air_travel_pkm": 1000.0,
            "supply_chain_freight_ton_km": 1000.0, "data_provenance": "SYNTHETIC_DEMO"
        },
        {
            "org_id": "TestOrg", "facility_id": "FAC-2", "year": 2022,
            "stationary_diesel_liters": 1000.0, "natural_gas_m3": 500.0, "fleet_transport_km": 1000.0,
            "purchased_electricity_kwh": 10000.0, "business_air_travel_pkm": 1000.0,
            "supply_chain_freight_ton_km": 1000.0, "data_provenance": "SYNTHETIC_DEMO"
        },
    ]
    state = {
        "org_name": "TestOrg", "target_entity": "India", "start_year": 2022, "end_year": 2022,
        "org_activity_records": facility_rows, "owid_benchmark_records": _mock_owid_records(2022, 2022), "agent_logs": []
    }
    res = calculation_agent(state)
    assert len(res["annual_emissions_records"]) == 1
    rec = res["annual_emissions_records"][0]
    assert round(rec["scope_1_tco2e"], 2) == 7.74
    assert round(rec["scope_2_tco2e"], 2) == 14.32
    assert round(rec["scope_3_tco2e"], 2) == 0.51
    assert round(rec["total_org_tco2e"], 2) == 22.57

def test_2_organization_separation_and_csv_org_mismatch_rejection(tmp_path):
    s_apex = ingestion_agent({"org_name": "Apex Manufacturing Pvt Ltd", "target_entity": "India", "start_year": 2015, "end_year": 2023, "agent_logs": []})
    s_green = ingestion_agent({"org_name": "GreenGrid Logistics Corp", "target_entity": "India", "start_year": 2015, "end_year": 2023, "agent_logs": []})
    assert s_apex["org_activity_records"][-1]["stationary_diesel_liters"] != s_green["org_activity_records"][-1]["stationary_diesel_liters"]

    # CSV with OtherCompany must NOT fall back to assigning OtherCompany rows to Apex!
    other_csv = tmp_path / "other_org.csv"
    pd.DataFrame([{
        "org_id": "OtherCompany", "facility_id": "F1", "year": 2022,
        "stationary_diesel_liters": 500.0, "natural_gas_m3": 200.0, "fleet_transport_km": 1000.0,
        "purchased_electricity_kwh": 5000.0, "business_air_travel_pkm": 300.0, "supply_chain_freight_ton_km": 800.0
    }]).to_csv(other_csv, index=False)

    res_mismatch = ingestion_agent({
        "org_name": "Apex Manufacturing Pvt Ltd", "target_entity": "India",
        "start_year": 2022, "end_year": 2022, "data_source_path": str(other_csv), "agent_logs": []
    })
    assert res_mismatch["ingestion_status"] == "FAILED"
    assert "not found" in res_mismatch["data_quality_report"]["error"]

def test_3_csv_quality_rejects_negative_duplicates_and_mixed_provenance(tmp_path):
    neg_csv = tmp_path / "neg.csv"
    pd.DataFrame([{
        "org_id": "Apex", "facility_id": "F1", "year": 2022,
        "stationary_diesel_liters": -100.0, "natural_gas_m3": 200.0, "fleet_transport_km": 1000.0,
        "purchased_electricity_kwh": 5000.0, "business_air_travel_pkm": 300.0, "supply_chain_freight_ton_km": 800.0
    }]).to_csv(neg_csv, index=False)
    r_neg = ingestion_agent({"org_name": "Apex", "target_entity": "India", "start_year": 2022, "end_year": 2022, "data_source_path": str(neg_csv), "agent_logs": []})
    assert r_neg["ingestion_status"] == "FAILED"
    assert "Negative" in r_neg["data_quality_report"]["error"]

    dup_csv = tmp_path / "dup.csv"
    row = {
        "org_id": "Apex", "facility_id": "F1", "year": 2022,
        "stationary_diesel_liters": 100.0, "natural_gas_m3": 200.0, "fleet_transport_km": 1000.0,
        "purchased_electricity_kwh": 5000.0, "business_air_travel_pkm": 300.0, "supply_chain_freight_ton_km": 800.0
    }
    pd.DataFrame([row, row]).to_csv(dup_csv, index=False)
    r_dup = ingestion_agent({"org_name": "Apex", "target_entity": "India", "start_year": 2022, "end_year": 2022, "data_source_path": str(dup_csv), "agent_logs": []})
    assert r_dup["ingestion_status"] == "FAILED"
    assert "Duplicate" in r_dup["data_quality_report"]["error"]

def test_4_short_time_series_eight_year_and_baseline_warning():
    state = ingestion_agent({"org_name": "Apex Manufacturing Pvt Ltd", "target_entity": "India", "start_year": 2015, "end_year": 2022, "agent_logs": []})
    state.update({"org_name": "Apex Manufacturing Pvt Ltd", "target_entity": "India", "start_year": 2015, "end_year": 2022})
    state.update(calculation_agent(state))
    ml_res = ml_engine_agent(state)
    metrics = ml_res["ml_evaluation_metrics"]
    assert metrics["status"] == "COMPLETED"
    assert metrics["walk_forward_folds"] >= 2
    assert metrics["forecast_horizon_label"].startswith("2023–")
    assert "worse_than_baseline" in metrics

def test_5_critic_rejects_missing_or_incorrect_figures():
    state = {
        "draft_report": "## 1. Executive Summary\nWrong total: 999999.99 tCO2e.",
        "computed_metrics": {"end_org_tco2e": 4215.63, "org_net_change_pct": 81.45, "owid_national_end_co2_mt": 3062.756, "data_provenance": "SYNTHETIC_DEMO"},
        "scope_breakdown": {"Scope 1": 1000.0, "Scope 2": 2000.0, "Scope 3": 1215.63}, "agent_logs": []
    }
    assert critic_agent(state)["critic_approved"] is False

def test_6_non_destructive_ledger_migration_and_scheduler_validation():
    # Create an old-schema automated_runs table without start_year/end_year
    conn = sqlite3.connect(main_mod.RUN_LEDGER_DB)
    conn.execute("""
        CREATE TABLE automated_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc TEXT NOT NULL, org_name TEXT NOT NULL, country TEXT NOT NULL,
            status TEXT NOT NULL, critic_approved INTEGER NOT NULL,
            faithfulness_score REAL NOT NULL, end_org_tco2e REAL, state_json TEXT
        )
    """)
    conn.execute("INSERT INTO automated_runs VALUES (1, '2026-01-01', 'LegacyOrg', 'India', 'COMPLETED', 1, 100.0, 123.4, '{}')")
    conn.commit()
    conn.close()

    # Running init_run_ledger must migrate columns WITHOUT deleting the LegacyOrg row!
    init_run_ledger()
    conn = sqlite3.connect(main_mod.RUN_LEDGER_DB)
    count = conn.execute("SELECT COUNT(*) FROM automated_runs WHERE org_name = 'LegacyOrg'").fetchone()[0]
    conn.close()
    assert count == 1

    # Scheduler parameter validation must reject non-positive intervals
    with pytest.raises(ValueError):
        validate_cli_parameters(2000, 2023, interval_minutes=0)
    with pytest.raises(ValueError):
        validate_cli_parameters(2023, 2000, interval_minutes=60)


def test_7_frontend_api_uses_pipeline_state(monkeypatch):
    state = _dashboard_state()
    run_args = {}

    def fake_run_pipeline(**kwargs):
        run_args.update(kwargs)
        return state

    monkeypatch.setattr(server_mod, "run_pipeline", fake_run_pipeline)
    client = TestClient(server_mod.app)

    page = client.get("/")
    assert page.status_code == 200
    assert "CARBON TRACE" in page.text
    assert client.get("/api/health").json()["status"] == "ok"

    latest = client.get("/api/run", params={
        "org_name": "Apex Manufacturing Pvt Ltd",
        "country": "India",
        "start_year": 2020,
        "end_year": 2023,
    })
    assert latest.status_code == 200
    assert latest.json()["metrics"]["end_org_tco2e"] == 4215.63
    assert latest.json()["corporate"]["cin_number"] == "L17110MH1973PLC019786"
    assert latest.json()["corporate"]["bse_code"] == "500325"
    assert latest.json()["corporate"]["nse_symbol"] == "RELIANCE"
    assert latest.json()["corporate"]["filing_section"] == "Section E: Principle 6"

    organizations = client.get("/api/organizations").json()["organizations"]
    assert "Reliance Industries Limited" in organizations
    assert "NTPC Limited" in organizations
    assert "Tata Steel Limited" in organizations

    response = client.post("/api/run", json={
        "org_name": "Apex Manufacturing Pvt Ltd",
        "country": "India",
        "start_year": 2020,
        "end_year": 2023,
    })
    assert response.status_code == 200
    assert response.json()["metrics"]["end_org_tco2e"] == 4215.63
    assert response.json()["history"][0]["year"] == 2023
    assert run_args["org_name"] == "Apex Manufacturing Pvt Ltd"
    assert run_args["start_year"] == 2020


def test_8_csv_api_passes_temporary_upload_to_pipeline(monkeypatch):
    state = _dashboard_state()
    upload_info = {}

    def fake_run_pipeline(**kwargs):
        path = kwargs["data_source_path"]
        upload_info["exists_during_run"] = os.path.exists(path)
        with open(path, "rb") as csv_file:
            upload_info["body"] = csv_file.read()
        upload_info["path"] = path
        return state

    monkeypatch.setattr(server_mod, "run_pipeline", fake_run_pipeline)
    client = TestClient(server_mod.app)
    csv_bytes = b"year,stationary_diesel_liters\n2023,100"
    response = client.post(
        "/api/run-csv?org_name=Apex%20Manufacturing%20Pvt%20Ltd&country=India&start_year=2023&end_year=2023",
        content=csv_bytes,
        headers={"Content-Type": "text/csv"},
    )

    assert response.status_code == 200
    assert upload_info["exists_during_run"] is True
    assert upload_info["body"] == csv_bytes
    assert not os.path.exists(upload_info["path"])


@pytest.mark.parametrize(
    ("company", "cin", "bse", "nse", "section"),
    [
        ("ITC Limited", "L16005WB1910PLC001985", "500875", "ITC", "Section C: Principle 6"),
        ("Reliance Industries Limited", "L17110MH1973PLC019786", "500325", "RELIANCE", "Section E: Principle 6"),
        ("NTPC Limited", "L40101DL1975GOI007966", "532555", "NTPC", "Section E: Principle 6"),
        ("Tata Steel Limited", "L27100MH1907PLC000260", "500470", "TATASTEEL", "Section E: Principle 6"),
    ],
)
def test_cin_registry_lookup(company, cin, bse, nse, section):
    metadata = lookup_cin_metadata(cin)
    assert metadata["org_name"] == company
    assert metadata["bse_code"] == bse
    assert metadata["nse_symbol"] == nse
    assert metadata["data_provenance"] == "SYNTHETIC_DEMO"
    assert metadata["filing_section"] == section


def test_cin_validation_rejects_malformed_identifiers():
    assert validate_cin("l17110mh1973plc019786") == "L17110MH1973PLC019786"
    with pytest.raises(ValueError, match="21-character"):
        validate_cin("L17110MH1973PLC01978")


def test_brsr_principle_6_text_and_pdf_extraction(monkeypatch):
    filing_text = """
    Section E: Principle 6
    Energy consumption (GJ) 1,000
    Scope 1 emissions (tCO2e) 123.45
    Scope 2 emissions (tCO2e) 67.89
    Section E: Principle 7
    Scope 1 emissions (tCO2e) 999
    """
    extracted = extract_brsr_principle_6_text(filing_text)
    assert extracted["filing_section"] == "Section E: Principle 6"
    assert extracted["energy_consumption_unit"] == "GJ"
    assert extracted["energy_consumption_kwh"] == 277778.0
    assert extracted["reported_scope_1_tco2e"] == 123.45
    assert extracted["reported_scope_2_tco2e"] == 67.89

    class FakePage:
        def extract_text(self):
            return filing_text

    class FakeReader:
        def __init__(self, _source):
            self.pages = [FakePage()]

    monkeypatch.setattr(brsr_mod, "PdfReader", FakeReader)
    pdf_extracted = brsr_mod.extract_brsr_pdf(b"%PDF-test")
    assert pdf_extracted["reported_scope_1_tco2e"] == 123.45
    assert pdf_extracted["reported_scope_2_tco2e"] == 67.89


def test_brsr_upload_api_passes_temporary_pdf_to_pipeline(monkeypatch):
    pipeline_state = _dashboard_state()
    upload_info = {}

    def fake_run_pipeline(**kwargs):
        path = kwargs["brsr_pdf_path"]
        upload_info["exists_during_run"] = os.path.exists(path)
        with open(path, "rb") as pdf_file:
            upload_info["body"] = pdf_file.read()
        return pipeline_state

    monkeypatch.setattr(server_mod, "run_pipeline", fake_run_pipeline)
    client = TestClient(server_mod.app)
    pdf_bytes = b"%PDF-1.4 test"
    response = client.post(
        "/api/run-brsr?org_name=Reliance%20Industries%20Limited&country=India&start_year=2020&end_year=2023",
        content=pdf_bytes,
        headers={"Content-Type": "application/pdf"},
    )

    assert response.status_code == 200
    assert upload_info["exists_during_run"] is True
    assert upload_info["body"] == pdf_bytes


def test_brsr_section_c_principle_6_text_extraction():
    filing_text = """
    Section C: Principle 6
    Total energy consumption (kWh) 50,000
    Scope 1 emissions (tCO2e) 450.25
    Scope 2 emissions (tCO2e) 820.75
    Section C: Principle 7
    Scope 1 emissions (tCO2e) 100
    """
    extracted = extract_brsr_principle_6_text(filing_text)
    assert extracted["filing_section"] == "Section C: Principle 6"
    assert extracted["energy_consumption_unit"] == "KWH"
    assert extracted["energy_consumption_kwh"] == 50000.0
    assert extracted["reported_scope_1_tco2e"] == 450.25
    assert extracted["reported_scope_2_tco2e"] == 820.75


def test_simulated_demo_orgs_unregistered():
    from agents.brsr_extractor import resolve_company_metadata
    assert resolve_company_metadata("Apex Manufacturing Pvt Ltd") is None
    assert resolve_company_metadata("GreenGrid Logistics Corp") is None


def test_cin_regex_validation():
    # Valid listed and unlisted Indian Corporate Identity Numbers
    valid_cins = [
        "L17110MH1973PLC019786",  # Reliance
        "L40101DL1975GOI007966",  # NTPC
        "L27100MH1907PLC000260",  # Tata Steel
        "u72200ka1999ptc025688",  # Lowercase unlisted private company
        "U74999DL2018PTC333333",  # Unlisted
    ]
    for cin in valid_cins:
        validated = validate_cin(cin)
        assert len(validated) == 21
        assert validated == cin.upper()

    # Invalid CINs
    invalid_cins = [
        "L17110MH1973PLC01978",   # 20 chars (too short)
        "L17110MH1973PLC0197866", # 22 chars (too long)
        "X17110MH1973PLC019786",  # Invalid prefix (must start with L or U)
        "123456789012345678901",  # All digits
        "",                       # Empty
        None,                     # None
    ]
    for inv in invalid_cins:
        with pytest.raises(ValueError):
            validate_cin(inv)


def test_brsr_digital_pdf_extraction():
    sample_pdf = os.path.join("data", "sample_reliance_brsr_p6.pdf")
    assert os.path.exists(sample_pdf), "Sample reliance BRSR PDF fixture must exist"

    extracted = brsr_mod.extract_brsr_pdf(sample_pdf)
    assert extracted["document_format"] == "NATIVE_DIGITAL_TEXT"
    assert extracted["extraction_engine"] == "pdfplumber+pypdf"
    assert extracted["pages_scanned"] >= 1
    assert extracted["cin_number"] == "L17110MH1973PLC019786"
    assert "Reliance" in extracted["company_name"]
    assert extracted["reported_scope_1_tco2e"] == 27650000.0
    assert extracted["reported_scope_2_tco2e"] == 9420000.0
    assert extracted["total_extracted_footprint_tco2e"] == 37070000.0
    assert extracted["energy_consumption_gj"] == 1125000000.0
    assert extracted["energy_consumption_kwh"] == 312500250000.0
    assert len(extracted["disclosures_matrix"]) >= 3
    assert any(d["parameter"] == "Scope 1 Direct GHG Emissions" for d in extracted["disclosures_matrix"])
    assert any(d["parameter"] == "Total Operational Energy Consumption" for d in extracted["disclosures_matrix"])


def test_brsr_scanned_ocr_fallback(monkeypatch):
    """Test that low character count (<150 chars/page) routes to SCANNED_IMAGE_OCR."""
    ocr_result_text = """
    Business Responsibility and Sustainability Report
    Name of the Company: Bharat Heavy Electricals Limited
    CIN: L74899DL1964GOI004281
    Section C: Principle 6
    Essential Indicator 1: Total energy consumed (GJ) 450,000
    Essential Indicator 7:
    Scope 1 emissions (tCO2e) 85,200.5
    Scope 2 emissions (tCO2e) 42,100.0
    Scope 3 emissions (tCO2e) 12,300.0
    Section C: Principle 7
    """

    class LowCharPage:
        def extract_text(self):
            return "Scan P1"  # Only 7 chars (< 150 chars/page)
        def extract_tables(self):
            return []

    class MockPdfPlumber:
        def __init__(self, _stream):
            self.pages = [LowCharPage()]
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(brsr_mod.pdfplumber, "open", MockPdfPlumber)
    monkeypatch.setattr(brsr_mod, "_run_ocr_on_pdf_bytes", lambda b: (ocr_result_text, []))

    extracted = brsr_mod.extract_brsr_pdf(b"%PDF-1.4 scanned mock")
    assert extracted["document_format"] == "SCANNED_IMAGE_OCR"
    assert "ocr" in extracted["extraction_engine"]
    assert extracted["cin_number"] == "L74899DL1964GOI004281"
    assert extracted["reported_scope_1_tco2e"] == 85200.5
    assert extracted["reported_scope_2_tco2e"] == 42100.0
    assert extracted["reported_scope_3_tco2e"] == 12300.0
    assert extracted["energy_consumption_gj"] == 450000.0
    assert extracted["total_extracted_footprint_tco2e"] == 139600.5


def test_brsr_end_to_end_pipeline_with_uploaded_pdf():
    from main import run_pipeline
    sample_pdf = os.path.join("data", "sample_reliance_brsr_p6.pdf")
    state = run_pipeline(
        org_name="Reliance Industries Limited",
        entity="India",
        start_year=2018,
        end_year=2023,
        brsr_pdf_path=sample_pdf
    )
    assert state["ingestion_status"] == "SUCCESS"
    assert state["critic_approved"] is True
    metrics = state["computed_metrics"]
    assert metrics["document_format"] == "NATIVE_DIGITAL_TEXT"
    assert metrics["reported_scope_1_tco2e"] == 27650000.0
    assert metrics["reported_scope_2_tco2e"] == 9420000.0
    assert metrics["total_extracted_footprint_tco2e"] == 37070000.0
    assert len(metrics["disclosures_matrix"]) >= 3


def test_itc_brsr_pdf_comprehensive_extraction():
    itc_pdf = os.path.join("data", "itc-r-and-a-brsr-2026.pdf")
    if not os.path.exists(itc_pdf):
        pytest.skip("ITC BRSR PDF file not present")

    extracted = brsr_mod.extract_brsr_pdf(itc_pdf)
    assert extracted["cin_number"] == "L16005WB1910PLC001985"
    assert "ITC" in extracted["company_name"]
    assert extracted["financial_year"] == "FY 2025-26"
    assert extracted["previous_financial_year"] == "FY 2024-25"
    assert "KPMG" in extracted["assurance_provider"]

    # Principle 6 Scope 1, 2, 3 figures
    assert extracted["reported_scope_1_tco2e"] == 1045000.0
    assert extracted["reported_scope_1_ktco2e"] == 1045.0
    assert extracted["reported_scope_2_tco2e"] == 170000.0
    assert extracted["scope_2_location_tco2e"] == 170000.0
    assert extracted["scope_2_market_tco2e"] == 151000.0
    assert extracted["reported_scope_3_tco2e"] == 1442000.0
    assert extracted["reported_scope_3_ktco2e"] == 1442.0

    # Principle 6 Energy figures
    assert extracted["energy_consumption_value"] == 24025.0
    assert extracted["energy_consumption_unit"] == "TJ"
    assert extracted["renewable_energy_tj"] == 12334.0
    assert extracted["non_renewable_energy_tj"] == 11691.0
    assert extracted["renewable_electricity_tj"] == 964.0
    assert extracted["renewable_fuel_tj"] == 11182.0
    assert extracted["non_renewable_electricity_tj"] == 761.0
    assert extracted["non_renewable_fuel_tj"] == 10930.0

    # Previous FY comparison data
    prev = extracted["previous_fy_data"]
    assert prev["financial_year"] == "FY 2024-25"
    assert prev["reported_scope_1_tco2e"] == 1101000.0
    assert prev["reported_scope_2_tco2e"] == 153000.0
    assert prev["reported_scope_3_tco2e"] == 1062000.0
    assert prev["total_energy_value"] == 25791.0
    assert prev["renewable_energy_tj"] == 13434.0
    assert prev["non_renewable_energy_tj"] == 12357.0


def test_api_endpoints_companies_and_uploads(monkeypatch):
    import api as api_mod
    client = TestClient(api_mod.app)

    # 1. Test /api/companies
    resp = client.get("/api/companies")
    assert resp.status_code == 200
    data = resp.json()
    assert "ITC Limited" in data["companies"]
    assert any(c["cin_number"] == "L16005WB1910PLC001985" for c in data["registry"])

    # 2. Test /api/upload-csv endpoint
    csv_payload = b"year,stationary_diesel_liters\n2022,250"
    upload_info = {}

    def fake_run(**kwargs):
        upload_info.update(kwargs)
        return _dashboard_state()

    monkeypatch.setattr(server_mod, "run_pipeline", fake_run)
    csv_resp = client.post(
        "/api/upload-csv?org_name=Apex%20Manufacturing%20Pvt%20Ltd&country=India&start_year=2020&end_year=2023",
        content=csv_payload,
        headers={"Content-Type": "text/csv"}
    )
    assert csv_resp.status_code == 200
    assert upload_info.get("data_source_path") is not None

    # 3. Test /api/upload-brsr-pdf endpoint
    pdf_resp = client.post(
        "/api/upload-brsr-pdf?org_name=ITC%20Limited&country=India&start_year=2020&end_year=2025",
        content=b"%PDF-1.4 test mock",
        headers={"Content-Type": "application/pdf"}
    )
    assert pdf_resp.status_code == 200
    assert "corporate" in pdf_resp.json()


def test_itc_end_to_end_pipeline_run():
    from main import run_pipeline
    state = run_pipeline(
        org_name="ITC Limited",
        entity="India",
        start_year=2015,
        end_year=2025
    )
    assert state["ingestion_status"] == "SUCCESS"
    assert state["critic_approved"] is True
    metrics = state["computed_metrics"]
    assert metrics["cin_number"] == "L16005WB1910PLC001985"
    assert metrics["bse_code"] == "500875"
    assert metrics["nse_symbol"] == "ITC"
    assert metrics["reported_scope_1_tco2e"] == 1045000.0
    assert metrics["reported_scope_2_tco2e"] == 170000.0
    assert metrics["reported_scope_3_tco2e"] == 1442000.0
    assert metrics["energy_consumption_value"] == 24025.0
    assert len(state["annual_emissions_records"]) >= 10
    assert len(state["forecast_records"]) >= 5


def test_ml_walk_forward_anti_leakage():
    """
    Mathematical Anti-Leakage Invariance Test:
    Ensures that mutating future out-of-fold ground truth records y[t+1:] has ZERO effect
    on the expanding-window walk-forward model trained strictly on historical data y[:t].
    """
    from agents.ml_engine import predict_walk_forward_fold
    records = [
        {"year": 2015 + i, "total_org_tco2e": 1000.0 + i * 50.0}
        for i in range(8)
    ]
    fold_idx = 5
    pred_orig = predict_walk_forward_fold(records, fold_index=fold_idx)

    # Mutate future ground-truth values (fold_idx + 1 onward) with arbitrary corrupted values
    corrupted_records = [dict(r) for r in records]
    corrupted_records[6]["total_org_tco2e"] = 99999999.0
    corrupted_records[7]["total_org_tco2e"] = -88888888.0
    pred_corrupted = predict_walk_forward_fold(corrupted_records, fold_index=fold_idx)

    assert pred_orig == pred_corrupted, (
        f"Data leakage detected! Mutation of future records changed fold prediction: "
        f"{pred_orig} != {pred_corrupted}"
    )


def test_scanned_image_ocr_pipeline(tmp_path, monkeypatch):
    """
    Raster Image OCR Fallback Integration Test:
    Creates an image-only PDF with zero digital text layer and verifies that the dual-engine
    pipeline accurately classifies it as SCANNED_IMAGE_OCR and executes the OCR route.
    """
    from PIL import Image, ImageDraw
    import agents.brsr_extractor as brsr_mod

    # Create a synthetic scanned document page
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((30, 30), "BRSR Environmental Disclosures", fill=(0, 0, 0))
    draw.text((30, 70), "Company: Scanned Testing Corp", fill=(0, 0, 0))
    draw.text((30, 110), "CIN: L12345MH2020PLC123456", fill=(0, 0, 0))
    draw.text((30, 150), "Section E: Principle 6", fill=(0, 0, 0))
    draw.text((30, 190), "Scope 1 emissions (tCO2e) 5000.0", fill=(0, 0, 0))
    draw.text((30, 230), "Scope 2 emissions (tCO2e) 2000.0", fill=(0, 0, 0))

    pdf_path = str(tmp_path / "scanned_invoice.pdf")
    img.save(pdf_path, "PDF")

    if not brsr_mod._configure_tesseract():
        mock_ocr = (
            "BRSR Environmental Disclosures\n"
            "Company: Scanned Testing Corp\n"
            "CIN: L12345MH2020PLC123456\n"
            "Section E: Principle 6\n"
            "Scope 1 emissions (tCO2e) 5000.0\n"
            "Scope 2 emissions (tCO2e) 2000.0\n"
        )
        monkeypatch.setattr(brsr_mod, "_run_ocr_on_pdf_bytes", lambda b: (mock_ocr, []))

    res = brsr_mod.extract_brsr_pdf(pdf_path)
    assert res["document_format"] == "SCANNED_IMAGE_OCR"
    assert "ocr" in res["extraction_engine"]
    assert res["pages_scanned"] >= 1
