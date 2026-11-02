import os
import pandas as pd
from state import CarbonAgentState

OWID_CSV_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
CACHE_DIR = "data"
CACHE_FILE = os.path.join(CACHE_DIR, "owid_co2_cache.csv")

REQUIRED_COLUMNS = [
    "country", "year", "iso_code", "population", "gdp",
    "co2", "co2_per_capita", "co2_per_gdp",
    "coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2",
    "methane", "nitrous_oxide", "primary_energy_consumption"
]

def ingestion_agent(state: CarbonAgentState) -> dict:
    entity = state["target_entity"]
    start_year = state["start_year"]
    end_year = state["end_year"]
    logs = state.get("agent_logs", [])
    notes = []

    logs.append(f"📥 [Ingestion Agent] Initiating data pipeline for '{entity}' ({start_year}-{end_year})...")

    # 1. Smart Caching Mechanism
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(CACHE_FILE):
        df = pd.read_csv(CACHE_FILE, low_memory=False)
        logs.append("⚡ [Ingestion Agent] Loaded OWID dataset from local high-speed cache.")
    else:
        logs.append("🌐 [Ingestion Agent] Downloading live OWID dataset from GitHub repository...")
        df = pd.read_csv(OWID_CSV_URL, low_memory=False)
        df.to_csv(CACHE_FILE, index=False)
        logs.append("💾 [Ingestion Agent] Cached dataset locally for future runs.")

    # 2. Filter by Entity and Timeframe
    available_cols = [c for c in REQUIRED_COLUMNS if c in df.columns]
    entity_df = df[df["country"].str.lower() == entity.lower()][available_cols].copy()

    if entity_df.empty:
        return {
            "raw_records": [],
            "data_quality_notes": [f"Entity '{entity}' not found in OWID dataset."],
            "ingestion_status": "FAILED",
            "agent_logs": logs + [f"❌ [Ingestion Agent] Entity '{entity}' not found!"]
        }

    entity_df = entity_df[(entity_df["year"] >= start_year) & (entity_df["year"] <= end_year)]
    entity_df = entity_df.sort_values("year").reset_index(drop=True)

    # 3. Automated Data Sanitization & Imputation
    numeric_cols = [c for c in available_cols if c not in ["country", "iso_code", "year"]]
    missing_before = int(entity_df[numeric_cols].isna().sum().sum())

    if missing_before > 0:
        # Linear interpolation for time-series continuity, then fill edges with 0
        entity_df[numeric_cols] = entity_df[numeric_cols].interpolate(method="linear", limit_direction="both").fillna(0.0)
        notes.append(f"Imputed {missing_before} missing data points using time-series linear interpolation.")
        logs.append(f"🧹 [Ingestion Agent] Sanitized dataset: Imputed {missing_before} NaN values via time-series interpolation.")
    else:
        notes.append("Zero missing values detected in the selected window.")

    records = entity_df.to_dict(orient="records")
    logs.append(f"✅ [Ingestion Agent] Successfully extracted {len(records)} annual records.")

    return {
        "raw_records": records,
        "data_quality_notes": notes,
        "ingestion_status": "SUCCESS",
        "agent_logs": logs
    }