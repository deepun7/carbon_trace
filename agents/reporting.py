import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from state import CarbonAgentState

load_dotenv()

def compile_deterministic_verified_report(state: CarbonAgentState, llm_summary: str = None) -> str:
    """Generates a deterministic Markdown report with honest boundary, baseline comparison, and provenance disclosures."""
    m = state.get("computed_metrics", {})
    s = state.get("scope_breakdown", {})
    ml = state.get("ml_evaluation_metrics", {})
    ef = state.get("emission_factors_audit", {})
    dq = state.get("data_quality_report", {})
    anoms = state.get("anomalies_detected", [])
    fc = state.get("forecast_records", [])

    provenance = m.get("data_provenance", "SYNTHETIC_DEMO")
    fac_count = m.get("facilities_aggregated", 1)
    horizon_label = ml.get("forecast_horizon_label", "Future Horizon")

    s1_val = list(s.values())[0] if len(s) > 0 else 0.0
    s2_val = list(s.values())[1] if len(s) > 1 else 0.0
    s3_val = list(s.values())[2] if len(s) > 2 else 0.0
    cin_number = m.get("cin_number") or "Not available"
    bse_code = m.get("bse_code") or "Not available"
    nse_symbol = m.get("nse_symbol") or "Not available"
    filing_section = m.get("filing_section") or "Not available"
    brsr_provenance = m.get("brsr_data_provenance") or "Not available"
    reported_scope_1 = m.get("reported_scope_1_tco2e")
    reported_scope_2 = m.get("reported_scope_2_tco2e")
    reported_scope_3 = m.get("reported_scope_3_tco2e")
    energy_value = m.get("energy_consumption_value")
    energy_report = (
        f"{energy_value} {m.get('energy_consumption_unit')} "
        f"({m.get('energy_consumption_kwh')} kWh)"
        if energy_value is not None else "Not present in the registry or uploaded filing"
    )
    scope_1_reconciliation = (
        f"{reported_scope_1} tCO2e; activity-based variance: "
        f"{m.get('scope_1_reconciliation_variance_tco2e')} tCO2e"
        if reported_scope_1 is not None else "Not reported; reconciliation unavailable"
    )
    scope_2_reconciliation = (
        f"{reported_scope_2} tCO2e; activity-based variance: "
        f"{m.get('scope_2_reconciliation_variance_tco2e')} tCO2e"
        if reported_scope_2 is not None else "Not reported; reconciliation unavailable"
    )
    scope_3_reconciliation = (
        f"{reported_scope_3} tCO2e; activity-based variance: "
        f"{m.get('scope_3_reconciliation_variance_tco2e')} tCO2e"
        if reported_scope_3 is not None else "Not reported / optional"
    )

    anom_rows = "\n".join(
        [f"| {a['year']} | {a['org_tco2e']} tCO2e | {a['org_yoy_pct']}% | {a['z_score']} | {a['type']} |" for a in anoms]
    ) or "| None | - | - | - | - |"

    fc_rows = "\n".join(
        [f"| {r['year']} | {r['predicted_org_tco2e']} tCO2e | {r['ci_lower_tco2e']} – {r['ci_upper_tco2e']} tCO2e |" for r in fc]
    ) or "| N/A | Short History | N/A |"

    llm_block = f"\n### Optional AI Executive Commentary\n> {llm_summary}\n" if llm_summary else ""

    if ml.get("status") == "SKIPPED_SHORT_HISTORY":
        ml_section = f"**ML Evaluation Status:** Skipped ({ml.get('reason')})"
    else:
        baseline_alert = (
            f"\n> ⚠️ **Baseline Comparison Warning:** {ml.get('baseline_comparison_note')}\n"
            if ml.get("worse_than_baseline")
            else f"\n> ✔️ **Baseline Comparison Note:** {ml.get('baseline_comparison_note')}\n"
        )
        ml_section = f"""{baseline_alert}
- **Walk-Forward Evaluation Window:** **{ml.get('test_period')}** (**{ml.get('walk_forward_folds')}** expanding one-step-ahead test folds).
- **Primary Model ({ml.get('forecast_model')}):** **RMSE = {ml.get('rmse_tco2e')} tCO2e**, **MAE = {ml.get('mae_tco2e')} tCO2e**, **MAPE = {ml.get('mape_pct')}%**, **Out-of-Sample R² (Variance Explained vs Mean Baseline, NOT Accuracy) = {ml.get('r2_score')}**.
- **Baseline Comparison ({ml.get('baseline_model')}):** **Naive RMSE = {ml.get('baseline_naive_rmse_tco2e')} tCO2e**, **Naive MAE = {ml.get('baseline_naive_mae_tco2e')} tCO2e**, **Naive MAPE = {ml.get('baseline_naive_mape_pct')}%** (RMSE Skill vs Baseline: **{ml.get('rmse_skill_over_naive_pct')}%**).
- **Anomaly Method Agreement ({ml.get('anomaly_model')}):** **Agreement F1 = {ml.get('consensus_f1_score')}** (Precision: `{ml.get('consensus_precision')}`, Recall: `{ml.get('consensus_recall')}`). *Note: This measures agreement between two unsupervised methods (Isolation Forest vs Z-Score), not ground-truth accuracy.*
- **Optional Exploratory Scope Pattern Grouping:** {ml.get('clustering_model')} Silhouette Score = **{ml.get('silhouette_score')}**."""

    return f"""# Automated Organizational Carbon Footprint & OWID Benchmark Report — {m.get('org_name')}

> **Data Provenance & Boundary Notice:** Organization activity records in this prototype report are **{provenance}** data (`{dq.get('organization_data_source')}`), aggregated across **{fac_count} facilities** for **{m.get('org_name')}**. Estimates reflect **included activity categories only** (stationary diesel/natural gas, diesel fleet, purchased grid electricity, business flights, and HGV road freight), not a complete corporate inventory. National macro benchmark data is sourced from the **Our World in Data (OWID) CO2 Dataset** for **{m.get('benchmark_country')}**.

## 1. Executive Summary & Corporate Carbon Trajectory
Between **{m.get('start_year')}** and **{m.get('end_year')}**, **{m.get('org_name')}** recorded a starting organizational footprint (across included categories) of **{m.get('start_org_tco2e')} tCO2e** and a latest annual footprint of **{m.get('end_org_tco2e')} tCO2e**, representing a net change of **{m.get('org_net_change_pct')}%** and a compound annual growth rate (CAGR) of **{m.get('org_cagr_pct')}%**. Cumulative emissions across the period totaled **{m.get('cumulative_org_tco2e')} tCO2e**.
{llm_block}
| Metric Category | Organizational Value ({m.get('org_name')}) | National OWID Benchmark ({m.get('benchmark_country')}) |
| :--- | :--- | :--- |
| **Data Provenance & Boundary** | **{provenance} ({fac_count} Facilities, Included Categories)** | **OWID National Macro Dataset** |
| **Latest Annual Emissions ({m.get('end_year')})** | **{m.get('end_org_tco2e')} tCO2e** | **{m.get('owid_national_end_co2_mt')} Mt CO2** |
| **Net Trajectory Change ({m.get('start_year')}–{m.get('end_year')})** | **{m.get('org_net_change_pct')}%** | **{m.get('owid_national_net_change_pct')}%** |
| **Compound Annual Growth Rate (CAGR)** | **{m.get('org_cagr_pct')}%** | **{m.get('owid_national_cagr_pct')}%** |
| **CAGR Decoupling Alpha** | **{m.get('cagr_decoupling_alpha_pct')}%** | Baseline Reference |

## 2. Included GHG Scope 1, 2 & 3 Activity Categories & Factor Citations
Facility-level operational inputs were aggregated by `(org_id, year)` and converted into **tCO2e** using documented conversion factors (Registry `{ef.get('registry_version')}`).
> **Static Reference Factor Limitation:** Static 2024 reference emission factors are applied across all historical years in this prototype for consistent trend comparison; formal historical regulatory accounting requires year-specific annual grid and fuel factors.
- **Scope 1 (Included Stationary & Fleet Combustion):** **{s1_val} tCO2e**
  - *Stationary Diesel:* `{ef.get('diesel_stationary', {}).get('value')} kg CO2e/L` — {ef.get('diesel_stationary', {}).get('source')} ({ef.get('diesel_stationary', {}).get('url')})
  - *Natural Gas:* `{ef.get('natural_gas', {}).get('value')} kg CO2e/m3` — {ef.get('natural_gas', {}).get('source')} ({ef.get('natural_gas', {}).get('url')})
  - *Fleet Transport (Assumed Diesel LCV Average):* `{ef.get('fleet_transport', {}).get('value')} kg CO2e/km` — {ef.get('fleet_transport', {}).get('source')}
- **Scope 2 (Purchased Electricity — Location-Based):** **{s2_val} tCO2e**
  - *Grid Emission Factor ({m.get('benchmark_country')}):* `{m.get('grid_ef_kg_per_kwh')} kg CO2e/kWh` — {m.get('grid_ef_source')} ({ef.get('grid_electricity', {}).get('url', 'Official Registry')})
- **Scope 3 (Included Business Air Travel & HGV Road Freight Only):** **{s3_val} tCO2e**
  - *Business Air Travel:* `{ef.get('business_flight', {}).get('value')} kg CO2e/pkm` — {ef.get('business_flight', {}).get('source')}
  - *HGV Road Freight:* `{ef.get('road_freight', {}).get('value')} kg CO2e/ton-km` — {ef.get('road_freight', {}).get('source')}

## 3. MCA CIN Registry & BRSR Principle 6 Provenance
- **Company:** {m.get('org_name')}
- **MCA CIN:** {cin_number}
- **BSE Code:** {bse_code}
- **NSE Symbol:** {nse_symbol}
- **Filing section:** {filing_section}
- **BRSR metadata provenance:** {brsr_provenance}
- **BRSR source:** {m.get('brsr_source') or 'Not available'}
- **Operational activity provenance:** {provenance} (generated demo activity is not a reported BRSR value)
- **Document format & extraction engine:** {m.get('document_format', 'NATIVE_DIGITAL_TEXT')} ({m.get('pages_scanned', 1)} pages, {m.get('extraction_engine', 'pdfplumber+pypdf')})
- **Reported energy consumption:** {energy_report}
- **Reported Scope 1 (BRSR):** {scope_1_reconciliation}
- **Reported Scope 2 (BRSR):** {scope_2_reconciliation}
- **Reported Scope 3 (BRSR):** {scope_3_reconciliation}
- **Total Extracted Footprint:** {m.get('total_extracted_footprint_tco2e')} tCO2e

## 4. National Benchmarking Against OWID Macro Telemetry
National territorial emissions for **{m.get('benchmark_country')}** from the Our World in Data (OWID) dataset reached **{m.get('owid_national_end_co2_mt')} Mt CO2** with a national CAGR of **{m.get('owid_national_cagr_pct')}%**. Organizational estimates (`tCO2e`) are maintained strictly separate from national macro totals (`Mt CO2`).

## 5. Walk-Forward Forecast ({horizon_label}) vs Baseline & Anomaly Method Agreement
{ml_section}

### Detected Statistical Volatility Outliers (`|Z| >= 1.65`)
| Year | Organizational Emissions | YoY Change | Z-Score | Classification |
| :--- | :--- | :--- | :--- | :--- |
{anom_rows}

### {horizon_label} Illustrative Walk-Forward Projection
*Note: Projections from limited annual observations are illustrative trend extrapolations. The error band (`±1.96 × Walk-Forward RMSE × √step`) is an approximate heuristic error band, not a formally calibrated 95% prediction interval.*
| Year | Projected Footprint | Approximate Error Band (±1.96 × RMSE × √step) |
| :--- | :--- | :--- |
{fc_rows}

## 6. Automated Decarbonization Roadmap & Scope Abatement Actions
1. **Scope 2 Renewable Electricity Procurement:** Transitioning purchased facility electricity (`{s2_val} tCO2e`) to renewable PPAs reduces location-based grid exposure (`{m.get('grid_ef_kg_per_kwh')} kg CO2e/kWh`).
2. **Scope 1 Thermal & Fleet Decarbonization:** Electrifying diesel commercial fleets and upgrading stationary combustion units across all **{fac_count} facilities**.
3. **Scope 3 Freight & Aviation Optimization:** Shifting HGV road freight (`0.10455 kg CO2e/ton-km`) to rail corridors and prioritizing virtual collaboration.
"""


def reporting_agent(state: CarbonAgentState) -> dict:
    logs = list(state.get("agent_logs", []))
    revision = state.get("revision_count", 0)
    use_llm = state.get("use_llm_narrative", False)
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    llm_summary = None
    if use_llm and api_key and revision == 0:
        try:
            logs.append("✍️ [Reporting Agent] Generating optional LLM executive summary...")
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=api_key)
            m = state.get("computed_metrics", {})
            resp = llm.invoke([
                SystemMessage(content="Write a concise 2-sentence executive summary using only the exact provided metrics."),
                HumanMessage(content=f"Org: {m.get('org_name')}, Provenance: {m.get('data_provenance')}, Latest: {m.get('end_org_tco2e')} tCO2e, Net Change: {m.get('org_net_change_pct')}%.")
            ])
            llm_summary = resp.content.strip()
        except Exception as e:
            logs.append(f"⚠️ [Reporting Agent] Optional LLM narrative skipped ({str(e)[:40]}).")

    logs.append("📄 [Reporting Agent] Compiling deterministic Markdown report with dynamic horizon & boundary disclosures...")
    report_md = compile_deterministic_verified_report(state, llm_summary=llm_summary)

    return {
        "draft_report": report_md,
        "revision_count": revision + 1,
        "agent_logs": logs
    }