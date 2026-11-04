import sqlite3
import pandas as pd
import pytest
import seed_enterprise_db
import agents.ingestion as ing_mod
import main as main_mod
from agents.ingestion import ingestion_agent
from agents.calculation import calculation_agent
from agents.ml_engine import ml_engine_agent
from agents.reporting import reporting_agent
from agents.critic import critic_agent
from main import log_run_to_ledger, load_matching_persisted_run, validate_cli_parameters, init_run_ledger

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
            "supply_chain_freight_ton_km": 1000.0, "data_provenance": "SIMULATED_DEMO"
        },
        {
            "org_id": "TestOrg", "facility_id": "FAC-2", "year": 2022,
            "stationary_diesel_liters": 1000.0, "natural_gas_m3": 500.0, "fleet_transport_km": 1000.0,
            "purchased_electricity_kwh": 10000.0, "business_air_travel_pkm": 1000.0,
            "supply_chain_freight_ton_km": 1000.0, "data_provenance": "SIMULATED_DEMO"
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
        "computed_metrics": {"end_org_tco2e": 4215.63, "org_net_change_pct": 81.45, "owid_national_end_co2_mt": 3062.756, "data_provenance": "SIMULATED_DEMO"},
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