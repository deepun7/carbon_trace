import numpy as np
import pandas as pd
from state import CarbonAgentState

def calculation_agent(state: CarbonAgentState) -> dict:
    records = state["raw_records"]
    logs = state.get("agent_logs", [])

    if not records:
        logs.append("⚠️ [Calculation Agent] Aborted: No records available to compute.")
        return {"computed_metrics": {}, "anomalies_detected": [], "scope_breakdown": {}, "agent_logs": logs}

    logs.append("🧮 [Calculation Agent] Executing GHG emission modeling & statistical anomaly detection...")
    df = pd.DataFrame(records)

    # 1. Core Trend & Growth Metrics (Million Tonnes CO2)
    start_co2 = float(df.iloc[0]["co2"])
    end_co2 = float(df.iloc[-1]["co2"])
    total_cumulative_co2 = float(df["co2"].sum())
    mean_annual_co2 = float(df["co2"].mean())
    
    n_years = max(1, int(df.iloc[-1]["year"] - df.iloc[0]["year"]))
    net_change_pct = ((end_co2 - start_co2) / start_co2 * 100) if start_co2 > 0 else 0.0
    cagr_pct = (((end_co2 / start_co2) ** (1 / n_years)) - 1) * 100 if start_co2 > 0 else 0.0

    # 2. GHG Protocol Corporate Proxy Mapping (Latest Year)
    latest = df.iloc[-1]
    # Scope 1 Proxy: Direct fossil combustion & industrial processes (Oil, Gas, Cement, Flaring)
    scope_1 = float(latest.get("oil_co2", 0) + latest.get("gas_co2", 0) + latest.get("cement_co2", 0) + latest.get("flaring_co2", 0))
    # Scope 2 Proxy: Coal & heavy grid power generation proxy
    scope_2 = float(latest.get("coal_co2", 0))
    # Scope 3 Proxy: Non-CO2 GHG supply chain/agricultural equivalents (Methane + Nitrous Oxide in MtCO2e)
    scope_3 = float(latest.get("methane", 0) + latest.get("nitrous_oxide", 0))

    scope_breakdown = {
        "Scope 1 (Direct Fuel & Process - Mt)": round(scope_1, 3),
        "Scope 2 (Grid & Coal Energy - Mt)": round(scope_2, 3),
        "Scope 3 (Methane & N2O Value Chain - MtCO2e)": round(scope_3, 3)
    }

    # 3. Statistical Z-Score Anomaly Detection on Year-over-Year (YoY) Changes
    df["yoy_change_pct"] = df["co2"].pct_change() * 100
    valid_yoy = df.dropna(subset=["yoy_change_pct"]).copy()

    anomalies = []
    if len(valid_yoy) >= 4:
        mean_yoy = valid_yoy["yoy_change_pct"].mean()
        std_yoy = valid_yoy["yoy_change_pct"].std()

        if std_yoy > 0:
            valid_yoy["z_score"] = (valid_yoy["yoy_change_pct"] - mean_yoy) / std_yoy
            # Flag anomalies where |Z-score| >= 1.65 (90% confidence outlier)
            outliers = valid_yoy[valid_yoy["z_score"].abs() >= 1.65]
            for _, row in outliers.iterrows():
                anomaly_type = "SURGE_SPIKE" if row["z_score"] > 0 else "SHARP_DROP"
                anomalies.append({
                    "year": int(row["year"]),
                    "co2_mt": round(float(row["co2"]), 2),
                    "yoy_change_pct": round(float(row["yoy_change_pct"]), 2),
                    "z_score": round(float(row["z_score"]), 2),
                    "type": anomaly_type
                })

    computed_metrics = {
        "start_year": int(df.iloc[0]["year"]),
        "end_year": int(df.iloc[-1]["year"]),
        "start_co2_mt": round(start_co2, 3),
        "end_co2_mt": round(end_co2, 3),
        "cumulative_co2_mt": round(total_cumulative_co2, 3),
        "mean_annual_co2_mt": round(mean_annual_co2, 3),
        "net_change_pct": round(net_change_pct, 2),
        "cagr_pct": round(cagr_pct, 2),
        "latest_co2_per_capita_t": round(float(latest.get("co2_per_capita", 0)), 3),
        "latest_energy_consumption_twh": round(float(latest.get("primary_energy_consumption", 0)), 2),
        "peak_emission_year": int(df.loc[df["co2"].idxmax()]["year"]),
        "peak_emission_mt": round(float(df["co2"].max()), 3)
    }

    logs.append(
        f"✅ [Calculation Agent] Computed metrics: Net Change = {computed_metrics['net_change_pct']}%, "
        f"CAGR = {computed_metrics['cagr_pct']}%, Anomalies Found = {len(anomalies)}."
    )

    return {
        "computed_metrics": computed_metrics,
        "anomalies_detected": anomalies,
        "scope_breakdown": scope_breakdown,
        "agent_logs": logs
    }