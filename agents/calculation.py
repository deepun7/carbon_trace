import json
import numpy as np
import pandas as pd
from state import CarbonAgentState
import seed_enterprise_db

NUMERIC_ACTIVITY_COLS = [
    "stationary_diesel_liters", "natural_gas_m3",
    "fleet_transport_km", "purchased_electricity_kwh",
    "business_air_travel_pkm", "supply_chain_freight_ton_km"
]

def calculation_agent(state: CarbonAgentState) -> dict:
    org_records = state.get("org_activity_records", [])
    owid_records = state.get("owid_benchmark_records", [])
    org_name = state.get("org_name", "Apex Manufacturing Pvt Ltd")
    entity = state["target_entity"]
    logs = list(state.get("agent_logs", []))

    if not org_records or not owid_records:
        logs.append("⚠️ [Calculation Agent] Aborted: Missing organization or OWID records.")
        return {
            "computed_metrics": {},
            "scope_breakdown": {},
            "emission_factors_audit": {},
            "annual_emissions_records": [],
            "anomalies_detected": [],
            "agent_logs": logs
        }

    seed_enterprise_db.initialize_enterprise_data_store()
    with open(seed_enterprise_db.EF_REGISTRY_PATH, "r", encoding="utf-8") as f:
        ef_registry = json.load(f)

    s1_ef = ef_registry["scope_1_factors"]
    s2_registry = ef_registry["scope_2_location_grid_factors_kg_co2e_per_kwh"]
    s3_ef = ef_registry["scope_3_factors"]

    grid_entry = s2_registry.get(entity, s2_registry["World"])
    grid_ef_val = float(grid_entry["value"])

    org_df = pd.DataFrame(org_records)
    if "org_id" not in org_df.columns:
        org_df["org_id"] = org_name

    org_df = org_df[org_df["org_id"].astype(str).str.lower() == org_name.lower()].copy()
    fac_count = int(org_df["facilities_aggregated"].max()) if "facilities_aggregated" in org_df.columns else (
        int(org_df["facility_id"].nunique()) if "facility_id" in org_df.columns else 1
    )
    provenance = str(org_df["data_provenance"].iloc[0]) if "data_provenance" in org_df.columns else "SIMULATED_DEMO"

    org_yearly = (
        org_df.groupby(["org_id", "year"], as_index=False)[NUMERIC_ACTIVITY_COLS]
        .sum()
        .sort_values("year")
        .reset_index(drop=True)
    )

    owid_df = pd.DataFrame(owid_records).drop_duplicates(subset=["year"]).sort_values("year")
    merged = pd.merge(org_yearly, owid_df, on="year", how="left")

    diesel_ef = float(s1_ef["diesel_stationary_kg_co2e_per_liter"]["value"])
    ng_ef = float(s1_ef["natural_gas_kg_co2e_per_m3"]["value"])
    fleet_ef = float(s1_ef["fleet_diesel_kg_co2e_per_km"]["value"])
    flight_ef = float(s3_ef["business_flight_short_medium_haul_kg_co2e_per_pkm"]["value"])
    freight_ef = float(s3_ef["road_freight_hgv_kg_co2e_per_ton_km"]["value"])

    merged["scope_1_diesel_tco2e"] = (merged["stationary_diesel_liters"] * diesel_ef) / 1000.0
    merged["scope_1_gas_tco2e"] = (merged["natural_gas_m3"] * ng_ef) / 1000.0
    merged["scope_1_fleet_tco2e"] = (merged["fleet_transport_km"] * fleet_ef) / 1000.0
    merged["scope_1_tco2e"] = (
        merged["scope_1_diesel_tco2e"] + merged["scope_1_gas_tco2e"] + merged["scope_1_fleet_tco2e"]
    )

    merged["scope_2_tco2e"] = (merged["purchased_electricity_kwh"] * grid_ef_val) / 1000.0

    merged["scope_3_flight_tco2e"] = (merged["business_air_travel_pkm"] * flight_ef) / 1000.0
    merged["scope_3_freight_tco2e"] = (merged["supply_chain_freight_ton_km"] * freight_ef) / 1000.0
    merged["scope_3_tco2e"] = merged["scope_3_flight_tco2e"] + merged["scope_3_freight_tco2e"]

    merged["total_org_tco2e"] = merged["scope_1_tco2e"] + merged["scope_2_tco2e"] + merged["scope_3_tco2e"]
    merged["org_yoy_pct"] = merged["total_org_tco2e"].pct_change() * 100.0
    merged["owid_national_yoy_pct"] = merged["co2"].pct_change() * 100.0

    latest = merged.iloc[-1]
    scope_breakdown = {
        "Scope 1: Stationary & Fleet Combustion (tCO2e)": round(float(latest["scope_1_tco2e"]), 2),
        "Scope 2: Purchased Electricity Location-Based (tCO2e)": round(float(latest["scope_2_tco2e"]), 2),
        "Scope 3: Business Air Travel & Road Freight (tCO2e)": round(float(latest["scope_3_tco2e"]), 2)
    }

    start_org = float(merged.iloc[0]["total_org_tco2e"])
    end_org = float(merged.iloc[-1]["total_org_tco2e"])
    n_years = max(1, int(merged.iloc[-1]["year"] - merged.iloc[0]["year"]))
    org_net_change_pct = ((end_org - start_org) / start_org) * 100.0 if start_org > 0 else 0.0
    org_cagr_pct = (((end_org / start_org) ** (1.0 / n_years)) - 1.0) * 100.0 if start_org > 0 else 0.0

    valid_owid = merged.dropna(subset=["co2"])
    start_owid = float(valid_owid.iloc[0]["co2"]) if not valid_owid.empty else 0.0
    end_owid = float(valid_owid.iloc[-1]["co2"]) if not valid_owid.empty else 0.0
    owid_net_change_pct = ((end_owid - start_owid) / start_owid) * 100.0 if start_owid > 0 else 0.0
    owid_cagr_pct = (((end_owid / start_owid) ** (1.0 / n_years)) - 1.0) * 100.0 if start_owid > 0 else 0.0

    valid_yoy = merged.dropna(subset=["org_yoy_pct"]).copy()
    anomalies = []
    if len(valid_yoy) >= 4:
        mean_yoy = valid_yoy["org_yoy_pct"].mean()
        std_yoy = valid_yoy["org_yoy_pct"].std()
        if std_yoy > 0:
            valid_yoy["z_score"] = (valid_yoy["org_yoy_pct"] - mean_yoy) / std_yoy
            outliers = valid_yoy[valid_yoy["z_score"].abs() >= 1.65]
            for _, row in outliers.iterrows():
                anomalies.append({
                    "year": int(row["year"]),
                    "org_tco2e": round(float(row["total_org_tco2e"]), 2),
                    "org_yoy_pct": round(float(row["org_yoy_pct"]), 2),
                    "z_score": round(float(row["z_score"]), 2),
                    "type": "SURGE_OUTLIER" if row["z_score"] > 0 else "CONTRACTION_OUTLIER"
                })

    ef_audit = {
        "registry_version": ef_registry["metadata"]["version"],
        "historical_applicability_note": ef_registry["metadata"].get("historical_applicability_note", ""),
        "diesel_stationary": s1_ef["diesel_stationary_kg_co2e_per_liter"],
        "natural_gas": s1_ef["natural_gas_kg_co2e_per_m3"],
        "fleet_transport": s1_ef["fleet_diesel_kg_co2e_per_km"],
        "grid_electricity": grid_entry,
        "business_flight": s3_ef["business_flight_short_medium_haul_kg_co2e_per_pkm"],
        "road_freight": s3_ef["road_freight_hgv_kg_co2e_per_ton_km"]
    }

    computed_metrics = {
        "org_name": org_name,
        "data_provenance": provenance,
        "facilities_aggregated": fac_count,
        "benchmark_country": entity,
        "start_year": int(merged.iloc[0]["year"]),
        "end_year": int(merged.iloc[-1]["year"]),
        "start_org_tco2e": round(start_org, 2),
        "end_org_tco2e": round(end_org, 2),
        "cumulative_org_tco2e": round(float(merged["total_org_tco2e"].sum()), 2),
        "org_net_change_pct": round(org_net_change_pct, 2),
        "org_cagr_pct": round(org_cagr_pct, 2),
        "owid_national_end_co2_mt": round(end_owid, 3),
        "owid_national_net_change_pct": round(owid_net_change_pct, 2),
        "owid_national_cagr_pct": round(owid_cagr_pct, 2),
        "cagr_decoupling_alpha_pct": round(org_cagr_pct - owid_cagr_pct, 2),
        "grid_ef_kg_per_kwh": grid_ef_val,
        "grid_ef_source": grid_entry["source"]
    }

    export_cols = [
        "org_id", "year", "scope_1_tco2e", "scope_2_tco2e", "scope_3_tco2e",
        "total_org_tco2e", "org_yoy_pct", "co2", "owid_national_yoy_pct"
    ]
    annual_records = merged[[c for c in export_cols if c in merged.columns]].round(3).to_dict(orient="records")

    logs.append(
        f"✅ [Calculation Agent] {org_name} ({provenance}, {fac_count} facilities): "
        f"Latest = {computed_metrics['end_org_tco2e']} tCO2e."
    )

    return {
        "computed_metrics": computed_metrics,
        "scope_breakdown": scope_breakdown,
        "emission_factors_audit": ef_audit,
        "annual_emissions_records": annual_records,
        "anomalies_detected": anomalies,
        "agent_logs": logs
    }