import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from main import run_pipeline, load_matching_persisted_run

load_dotenv()

st.set_page_config(
    page_title="CARBONTRACE // MULTI-AGENT PROTOTYPE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Space+Grotesk:wght@400;600;700&display=swap');

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #080808 !important;
        color: #F0F0F0 !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #0D0D0D !important;
        border-right: 1px solid #7FFF0040 !important;
    }

    h1 {
        color: #7FFF00 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        text-shadow: 0 0 18px rgba(127, 255, 0, 0.25);
    }

    h2, h3, h4 {
        color: #FFFFFF !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-left: 4px solid #FF1E42;
        padding-left: 10px;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #0F0F0F, #141414) !important;
        border: 1px solid #262626 !important;
        border-top: 3px solid #7FFF00 !important;
        border-radius: 8px !important;
        padding: 16px 20px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #A0A0A0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #7FFF00 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800 !important;
        font-size: 1.55rem !important;
    }

    [data-testid="stMetricDelta"] {
        color: #FF1E42 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
    }

    .stButton > button, .stDownloadButton > button {
        background: #FF1E42 !important;
        color: #FFFFFF !important;
        border: 1px solid #FF1E42 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        border-radius: 6px !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #7FFF00 !important;
        color: #080808 !important;
        border: 1px solid #7FFF00 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #7FFF00 !important;
        color: #080808 !important;
        font-weight: 800 !important;
    }

    .tactical-card {
        background-color: #101010;
        border: 1px solid #262626;
        border-left: 4px solid #7FFF00;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
        font-family: 'JetBrains Mono', monospace;
    }

    .tactical-card-red {
        background-color: #101010;
        border: 1px solid #262626;
        border-left: 4px solid #FF1E42;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='border-left:4px solid #7FFF00;'>⚙️ PROTOTYPE CONTROLS</h2>", unsafe_allow_html=True)

    org_name = st.selectbox(
        "SELECT ORGANIZATION (SIMULATED DB)",
        ["Apex Manufacturing Pvt Ltd", "GreenGrid Logistics Corp"],
        index=0
    )
    entity = st.selectbox(
        "OWID BENCHMARK COUNTRY",
        ["India", "United States", "China", "European Union (27)", "United Kingdom", "Germany", "Japan", "World"],
        index=0
    )
    year_range = st.slider("EVALUATION PERIOD", min_value=2000, max_value=2023, value=(2000, 2023))

    uploaded_csv = st.file_uploader("OPTIONAL EXTERNAL ACTIVITY CSV", type=["csv"])
    custom_csv_path = None
    if uploaded_csv is not None:
        os.makedirs("data", exist_ok=True)
        custom_csv_path = os.path.join("data", "uploaded_erp_activity.csv")
        with open(custom_csv_path, "wb") as f:
            f.write(uploaded_csv.getbuffer())

    use_llm = st.checkbox("Include Optional LLM Executive Summary", value=False)
    run_btn = st.button("🔄 RUN / REFRESH PIPELINE", use_container_width=True)

selection_key = f"{org_name}_{entity}_{year_range[0]}_{year_range[1]}_{bool(custom_csv_path)}_{use_llm}"

if run_btn or st.session_state.get("selection_key") != selection_key:
    matched_run = None if (run_btn or custom_csv_path) else load_matching_persisted_run(
        org_name, entity, year_range[0], year_range[1]
    )
    if matched_run:
        st.session_state["active_state"] = matched_run
    else:
        with st.spinner(f"⚡ RUNNING 5-AGENT PROTOTYPE PIPELINE FOR [{org_name}] ({year_range[0]}–{year_range[1]})..."):
            st.session_state["active_state"] = run_pipeline(
                entity=entity,
                start_year=year_range[0],
                end_year=year_range[1],
                org_name=org_name,
                data_source_path=custom_csv_path,
                use_llm_narrative=use_llm
            )
    st.session_state["selection_key"] = selection_key

state = st.session_state["active_state"]

if state["ingestion_status"] != "SUCCESS":
    st.error(f"PIPELINE ERROR: {state['data_quality_report']}")
    st.stop()

metrics = state["computed_metrics"]
ml = state["ml_evaluation_metrics"]
dq = state["data_quality_report"]
annual_df = pd.DataFrame(state["annual_emissions_records"])
org_raw_df = pd.DataFrame(state["org_activity_records"])
forecast_df = pd.DataFrame(state["forecast_records"])
anomalies = state["anomalies_detected"]
scopes = state["scope_breakdown"]
ef_audit = state.get("emission_factors_audit", {})

last_ts = state.get("_last_run_timestamp_utc", "Just now")
provenance_badge = dq.get("data_provenance", "SIMULATED_DEMO")
horizon_label = ml.get("forecast_horizon_label", "Future Horizon")

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; border-bottom: 2px solid #222; padding-bottom: 10px; margin-bottom: 16px;">
    <div>
        <h1 style="margin:0;">⚡ CARBONTRACE // MULTI-AGENT PROTOTYPE</h1>
        <p style="margin:0; color:#AAA; font-family:'JetBrains Mono', monospace; font-size:0.85rem;">
            ORG: <b style="color:#7FFF00;">{metrics['org_name']} ({dq.get('facilities_aggregated', 1)} Facilities, Included Categories)</b> •
            PERIOD: <b style="color:#FFF;">{metrics['start_year']}–{metrics['end_year']}</b> •
            BENCHMARK: <b style="color:#FF1E42;">{metrics['benchmark_country']} (OWID)</b>
        </p>
    </div>
    <div style="text-align:right; font-family:'JetBrains Mono', monospace; font-size:0.8rem;">
        <div style="background:#141414; border:1px solid #FF1E42; color:#FF1E42; padding:4px 10px; border-radius:4px; margin-bottom:4px;">
            DATA SOURCE: {provenance_badge}
        </div>
        <div style="color:#7FFF00;">LAST RUN: {last_ts}</div>
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("INCLUDED ORG FOOTPRINT", f"{metrics['end_org_tco2e']:,.1f} tCO₂e", f"{metrics['org_net_change_pct']:+.2f}% ({provenance_badge})")
c2.metric("WALK-FORWARD vs NAIVE RMSE", f"{ml.get('rmse_tco2e', 'N/A')} tCO₂e", f"Naive: {ml.get('baseline_naive_rmse_tco2e', 'N/A')} tCO₂e")
c3.metric("METHOD AGREEMENT (F1)", f"{ml.get('consensus_f1_score', 'N/A')}", "IsoForest vs Z-Score Agreement")
c4.metric("CRITIC COMPLETENESS CHECK", f"{state['faithfulness_score']}%", f"OWID: {metrics['owid_national_end_co2_mt']:,.1f} Mt")

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ WALK-FORWARD vs BASELINE ML",
    "🔥 INCLUDED SCOPES & OWID BENCHMARK",
    "📄 GENERATED PROTOTYPE REPORT",
    "🗄️ AGGREGATED TELEMETRY & EF CITATIONS"
])

with tab1:
    if ml.get("worse_than_baseline"):
        st.warning(f"⚠️ **Baseline Comparison Notice:** {ml.get('baseline_comparison_note')}")

    st.subheader(f"INCLUDED ORG EMISSIONS ({metrics['start_year']}–{metrics['end_year']}) & ILLUSTRATIVE PROJECTION ({horizon_label})")
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(x=annual_df["year"], y=annual_df["total_org_tco2e"], mode="lines+markers", name="Included Org Emissions (tCO₂e)", line=dict(color="#7FFF00", width=3.5)))
    if not forecast_df.empty:
        fig_fc.add_trace(go.Scatter(x=forecast_df["year"], y=forecast_df["predicted_org_tco2e"], mode="lines+markers", name=f"Illustrative Walk-Forward Projection ({horizon_label})", line=dict(color="#FF1E42", width=3.5, dash="dash")))
        fig_fc.add_trace(go.Scatter(
            x=list(forecast_df["year"]) + list(forecast_df["year"])[::-1],
            y=list(forecast_df["ci_upper_tco2e"]) + list(forecast_df["ci_lower_tco2e"])[::-1],
            fill="toself", fillcolor="rgba(255, 30, 66, 0.16)", line=dict(color="rgba(0,0,0,0)"), name="Approximate Error Band (±1.96×RMSE×√step)"
        ))
    if anomalies:
        anom_df = pd.DataFrame(anomalies)
        fig_fc.add_trace(go.Scatter(x=anom_df["year"], y=anom_df["org_tco2e"], mode="markers", name="Z-Score Outlier Candidate (|Z| ≥ 1.65)", marker=dict(color="#FF1E42", size=15, symbol="star")))
    fig_fc.update_layout(template="plotly_dark", paper_bgcolor="#0C0C0C", plot_bgcolor="#0C0C0C", height=420, font=dict(family="JetBrains Mono, monospace"))
    st.plotly_chart(fig_fc, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="tactical-card">
            <div style="color:#7FFF00; font-weight:800;">01 // WALK-FORWARD vs NAIVE BASELINE</div>
            <div style="color:#AAA; font-size:0.8rem;">TEST PERIOD: {ml.get('test_period', 'N/A')} ({ml.get('walk_forward_folds', 0)} Folds)</div>
            <hr style="margin:8px 0;">
            <div>RIDGE WALK-FORWARD RMSE: <b style="color:#7FFF00; float:right;">{ml.get('rmse_tco2e', 'N/A')} tCO₂e</b></div>
            <div>NAIVE BASELINE RMSE: <b style="color:#FFF; float:right;">{ml.get('baseline_naive_rmse_tco2e', 'N/A')} tCO₂e</b></div>
            <div>R² (VAR vs MEAN) / MAPE: <b style="color:#FF1E42; float:right;">{ml.get('r2_score', 'N/A')} / {ml.get('mape_pct', 'N/A')}%</b></div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="tactical-card-red">
            <div style="color:#FF1E42; font-weight:800;">02 // INTER-METHOD AGREEMENT</div>
            <div style="color:#AAA; font-size:0.8rem;">IsoForest vs Z-Score (Not Ground Truth)</div>
            <hr style="margin:8px 0;">
            <div>METHOD AGREEMENT F1: <b style="color:#7FFF00; float:right;">{ml.get('consensus_f1_score', 'N/A')}</b></div>
            <div>AGREEMENT PRECISION: <b style="color:#FFF; float:right;">{ml.get('consensus_precision', 'N/A')}</b></div>
            <div>EXPLORATORY K-MEANS SILHOUETTE: <b style="color:#7FFF00; float:right;">{ml.get('silhouette_score', 'N/A')}</b></div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="tactical-card">
            <div style="color:#7FFF00; font-weight:800;">03 // BOUNDARY & OWID BENCHMARK</div>
            <div style="color:#AAA; font-size:0.8rem;">PROVENANCE: {provenance_badge}</div>
            <hr style="margin:8px 0;">
            <div>FACILITIES AGGREGATED: <b style="color:#7FFF00; float:right;">{dq.get('facilities_aggregated', 1)}</b></div>
            <div>OWID NATIONAL CO₂: <b style="color:#FFF; float:right;">{metrics['owid_national_end_co2_mt']} Mt</b></div>
            <div>STATIC 2024 GRID EF: <b style="color:#FF1E42; float:right;">{metrics['grid_ef_kg_per_kwh']} kg/kWh</b></div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.caption("Note: Static 2024 reference emission factors are applied across historical years for prototype trend consistency.")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("INCLUDED SCOPE 1, 2 & 3 BREAKDOWN (tCO₂e)")
        scope_df = pd.DataFrame({"Scope": list(scopes.keys()), "tCO2e": list(scopes.values())})
        fig_pie = px.pie(scope_df, names="Scope", values="tCO2e", hole=0.55, color_discrete_sequence=["#7FFF00", "#FF1E42", "#2E2E2E"])
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor="#0C0C0C", plot_bgcolor="#0C0C0C", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_b:
        st.subheader("ORG YoY (%) vs OWID NATIONAL YoY (%)")
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(x=annual_df["year"], y=annual_df["org_yoy_pct"], name="Organization YoY (%)", marker_color="#7FFF00"))
        fig_cmp.add_trace(go.Scatter(x=annual_df["year"], y=annual_df["owid_national_yoy_pct"], mode="lines+markers", name="OWID National YoY (%)", line=dict(color="#FF1E42", width=2.5)))
        fig_cmp.update_layout(template="plotly_dark", paper_bgcolor="#0C0C0C", plot_bgcolor="#0C0C0C", height=400)
        st.plotly_chart(fig_cmp, use_container_width=True)

with tab3:
    st.download_button("📥 DOWNLOAD GENERATED REPORT (.MD)", data=state["draft_report"], file_name="sample_generated_report.md", mime="text/markdown")
    st.markdown(state["draft_report"])

with tab4:
    st.subheader("DOCUMENTED EMISSION FACTOR REGISTRY & CITATIONS")
    st.json(ef_audit)
    st.subheader("DATA SOURCE & PROVENANCE AUDIT")
    st.json(dq)
    st.subheader("AGGREGATED ORGANIZATIONAL ACTIVITY (GROUPED BY ORG_ID & YEAR)")
    st.dataframe(org_raw_df, use_container_width=True)