import os
import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from main import run_pipeline, load_matching_persisted_run
from agents.brsr_extractor import resolve_company_metadata, extract_brsr_pdf

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
        "SELECT ORGANIZATION",
        [
            "Apex Manufacturing Pvt Ltd", "GreenGrid Logistics Corp",
            "Reliance Industries Limited", "NTPC Limited", "Tata Steel Limited",
        ],
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

    uploaded_brsr_pdf = st.file_uploader(
        "📄 UPLOAD BRSR PDF (ANY COMPANY / ANY YEAR)",
        type=["pdf"],
        help="Universal SEBI BRSR Parser: Any Indian corporate BRSR filing, digital or scanned OCR."
    )
    use_llm = st.checkbox("Include Optional LLM Executive Summary", value=False)
    run_btn = st.button("🔄 RUN / REFRESH PIPELINE", use_container_width=True)

selection_key = (
    f"{org_name}_{entity}_{year_range[0]}_{year_range[1]}_{bool(custom_csv_path)}_"
    f"{uploaded_brsr_pdf.name if uploaded_brsr_pdf else ''}_{use_llm}"
)

if run_btn or st.session_state.get("selection_key") != selection_key:
    matched_run = None if (run_btn or custom_csv_path or uploaded_brsr_pdf) else load_matching_persisted_run(
        org_name, entity, year_range[0], year_range[1]
    )
    if matched_run:
        st.session_state["active_state"] = matched_run
    else:
        brsr_pdf_path = None
        target_org = org_name
        target_cin = None
        if uploaded_brsr_pdf is not None:
            with tempfile.NamedTemporaryFile(prefix="carbontrace_brsr_", suffix=".pdf", delete=False) as pdf_file:
                pdf_file.write(uploaded_brsr_pdf.getvalue())
                brsr_pdf_path = pdf_file.name
            try:
                extracted_quick = extract_brsr_pdf(brsr_pdf_path)
                if extracted_quick.get("company_name") and (org_name == "Apex Manufacturing Pvt Ltd" or not org_name):
                    target_org = extracted_quick["company_name"]
                if extracted_quick.get("cin_number"):
                    target_cin = extracted_quick["cin_number"]
            except Exception:
                pass
        company_metadata = resolve_company_metadata(target_org, target_cin)
        if not target_cin and company_metadata:
            target_cin = company_metadata.get("cin_number")
        try:
            with st.spinner(f"⚡ RUNNING 5-AGENT PROTOTYPE PIPELINE FOR [{target_org}] ({year_range[0]}–{year_range[1]})..."):
                st.session_state["active_state"] = run_pipeline(
                    entity=entity,
                    start_year=year_range[0],
                    end_year=year_range[1],
                    org_name=target_org,
                    data_source_path=custom_csv_path,
                    use_llm_narrative=use_llm,
                    cin_number=target_cin,
                    brsr_pdf_path=brsr_pdf_path
                )
        finally:
            if brsr_pdf_path and os.path.exists(brsr_pdf_path):
                os.remove(brsr_pdf_path)
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
cin_number = metrics.get("cin_number") or "Not registered"
bse_code = metrics.get("bse_code") or "Not registered"
nse_symbol = metrics.get("nse_symbol") or "Not registered"
brsr_status = metrics.get("brsr_data_provenance") or "No BRSR registry record"
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
        <p style="margin:4px 0 0; color:#AAA; font-family:'JetBrains Mono', monospace; font-size:0.75rem;">
            MCA CIN: <b style="color:#FFF;">{cin_number}</b> • BSE: <b style="color:#FFF;">{bse_code}</b> •
            NSE: <b style="color:#FFF;">{nse_symbol}</b> •
            <b style="color:#7FFF00;">BRSR {metrics.get('filing_section') or 'status unavailable'}: {brsr_status}</b>
        </p>
    </div>
    <div style="text-align:right; font-family:'JetBrains Mono', monospace; font-size:0.8rem;">
        <div style="background:#141414; border:1px solid #FF1E42; color:#FF1E42; padding:4px 10px; border-radius:4px; margin-bottom:4px;">
            DATA SOURCE: {provenance_badge}
        </div>
        <div style="background:#141414; border:1px solid #7FFF00; color:#7FFF00; padding:4px 10px; border-radius:4px; margin-bottom:4px;">
            BRSR STATUS: {metrics.get('filing_section') or 'Unavailable'} — {brsr_status}
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
    doc_format = metrics.get("document_format") or "NATIVE_DIGITAL_TEXT"
    pages_scanned = metrics.get("pages_scanned", 1)
    engine = metrics.get("extraction_engine", "Digital Text Layer")
    fy = metrics.get("financial_year", "FY 2022-23")
    filing_sec = metrics.get("filing_section") or "Section C / E: Principle 6 (Environment)"

    st.markdown(f"""
    <div style="background:#121212; border:1px solid #7FFF00; border-radius:8px; padding:14px 18px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="background:#7FFF0025; border:1px solid #7FFF00; color:#7FFF00; font-size:0.8rem; padding:3px 10px; border-radius:4px; font-weight:800; font-family:'JetBrains Mono', monospace;">
                    {doc_format}
                </span>
                <span style="color:#FFF; font-weight:700; font-size:1.15rem; margin-left:10px; font-family:'JetBrains Mono', monospace;">
                    {metrics['org_name']} — {fy}
                </span>
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.82rem; color:#A0A0A0;">
                MCA CIN: <b style="color:#FFF;">{cin_number}</b> • SECTION: <b style="color:#7FFF00;">{filing_sec}</b> • PAGES: <b style="color:#FFF;">{pages_scanned} ({engine})</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Extracted KPI Cards
    bk1, bk2, bk3, bk4 = st.columns(4)
    s1_reported = metrics.get("reported_scope_1_tco2e")
    s2_reported = metrics.get("reported_scope_2_tco2e")
    s3_reported = metrics.get("reported_scope_3_tco2e")
    tot_extracted = metrics.get("total_extracted_footprint_tco2e") or (
        (s1_reported or 0.0) + (s2_reported or 0.0) + (s3_reported or 0.0)
    )
    energy_val = metrics.get("energy_consumption_value")
    energy_unit = metrics.get("energy_consumption_unit", "GJ")
    energy_gj = metrics.get("energy_consumption_gj") or energy_val
    energy_kwh = metrics.get("energy_consumption_kwh")

    bk1.metric("TOTAL EXTRACTED FOOTPRINT", f"{tot_extracted:,.1f} tCO₂e" if tot_extracted else "N/A", "Scope 1 + Scope 2 (+ Scope 3)")
    bk2.metric("SCOPE 1 DIRECT EMISSIONS", f"{s1_reported:,.1f} tCO₂e" if s1_reported is not None else "N/A (Simulated)", "Essential Indicator 7")
    bk3.metric("SCOPE 2 LOCATION-BASED", f"{s2_reported:,.1f} tCO₂e" if s2_reported is not None else "N/A (Simulated)", "Essential Indicator 7 (Grid)")
    bk4.metric(
        "TOTAL ENERGY CONSUMED",
        f"{energy_gj:,.1f} GJ" if energy_gj is not None else "N/A",
        f"≡ {energy_kwh:,.1f} kWh" if energy_kwh is not None else "Normalized GJ / kWh"
    )

    st.markdown("<hr style='border-color:#222; margin:16px 0;'>", unsafe_allow_html=True)

    # Interactive Scope Donut Chart & National Benchmark Comparison
    col_chart, col_bench = st.columns(2)
    with col_chart:
        st.subheader("📊 SCOPE 1 vs SCOPE 2 vs SCOPE 3 BREAKDOWN")
        chart_data = {
            "Scope 1 (Direct)": s1_reported if s1_reported is not None else list(scopes.values())[0],
            "Scope 2 (Purchased Electricity)": s2_reported if s2_reported is not None else list(scopes.values())[1],
            "Scope 3 (Value Chain / Logistics)": s3_reported if s3_reported is not None else (list(scopes.values())[2] if len(scopes) > 2 else 0.0),
        }
        fig_donut = go.Figure(data=[go.Pie(
            labels=list(chart_data.keys()),
            values=list(chart_data.values()),
            hole=0.6,
            marker_colors=["#C8792C", "#F4D9A0", "#5B4632"]
        )])
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0C0C0C",
            plot_bgcolor="#0C0C0C",
            height=320,
            font=dict(family="JetBrains Mono, monospace")
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_bench:
        st.subheader(f"🌐 NATIONAL BENCHMARK COMPARISON ({metrics['benchmark_country']})")
        org_s12 = (s1_reported or list(scopes.values())[0]) + (s2_reported or list(scopes.values())[1])
        owid_nat_mt = float(metrics.get("owid_national_end_co2_mt") or 0.0)
        owid_nat_tco2e = owid_nat_mt * 1_000_000.0
        share_nat_pct = (org_s12 / owid_nat_tco2e * 100.0) if owid_nat_tco2e > 0 else 0.0

        st.markdown(f"""
        <div class="tactical-card" style="padding:16px; margin-top:10px;">
            <div style="font-size:0.85rem; color:#A0A0A0;">VERIFIED CORPORATE SCOPE 1+2 FOOTPRINT</div>
            <div style="font-size:1.6rem; font-weight:800; color:#7FFF00; margin:4px 0;">{org_s12:,.1f} tCO₂e</div>
            <div style="font-size:0.85rem; color:#A0A0A0; margin-top:10px;">OWID NATIONAL BENCHMARK ({metrics['benchmark_country']} {metrics['end_year']})</div>
            <div style="font-size:1.4rem; font-weight:700; color:#F4D9A0; margin:4px 0;">{owid_nat_mt:,.1f} Mt CO₂ (≡ {owid_nat_tco2e:,.0f} tCO₂e)</div>
            <hr style="border-color:#333; margin:10px 0;">
            <div style="font-size:0.85rem; color:#FFF;">
                Corporate Footprint accounts for <b style="color:#C8792C;">{share_nat_pct:.4f}%</b> of {metrics['benchmark_country']}'s national greenhouse emissions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📋 AUDITED PARAMETER DISCLOSURES MATRIX (SEBI PRINCIPLE 6)")
    matrix_records = metrics.get("disclosures_matrix") or []
    if matrix_records:
        matrix_df = pd.DataFrame([
            {
                "Parameter": r.get("parameter"),
                "SEBI BRSR Indicator": r.get("indicator"),
                "Reported Value": f"{r.get('original_value'):,.1f} {r.get('reported_unit')}",
                "Standardized Value": f"{r.get('standardized_value'):,.1f} {r.get('standardized_unit')}",
            }
            for r in matrix_records
        ])
        st.dataframe(matrix_df, use_container_width=True)
    else:
        st.info("No structured BRSR disclosures matrix available for this simulated run. Upload an official BRSR PDF above to populate this matrix.")

    st.subheader("⚖️ BRSR PRINCIPLE 6 RECONCILIATION & VARIANCE AUDIT")
    s1_variance = metrics.get("scope_1_reconciliation_variance_tco2e")
    s2_variance = metrics.get("scope_2_reconciliation_variance_tco2e")
    s3_variance = metrics.get("scope_3_reconciliation_variance_tco2e")

    recon_data = [
        {
            "Scope": "Scope 1 (Direct Fuel & Fleet)",
            "BRSR Official Reported": f"{s1_reported:,.1f} tCO₂e" if s1_reported is not None else "N/A (Demo)",
            "Model Activity-Based": f"{list(scopes.values())[0]:,.1f} tCO₂e" if scopes else "N/A",
            "Variance (Model - Reported)": f"{s1_variance:+,.1f} tCO₂e" if s1_variance is not None else "N/A",
            "Filing Source": filing_sec
        },
        {
            "Scope": "Scope 2 (Purchased Grid Electricity)",
            "BRSR Official Reported": f"{s2_reported:,.1f} tCO₂e" if s2_reported is not None else "N/A (Demo)",
            "Model Activity-Based": f"{list(scopes.values())[1]:,.1f} tCO₂e" if len(scopes) > 1 else "N/A",
            "Variance (Model - Reported)": f"{s2_variance:+,.1f} tCO₂e" if s2_variance is not None else "N/A",
            "Filing Source": filing_sec
        }
    ]
    if s3_reported is not None:
        recon_data.append({
            "Scope": "Scope 3 (Value Chain / Logistics)",
            "BRSR Official Reported": f"{s3_reported:,.1f} tCO₂e",
            "Model Activity-Based": f"{list(scopes.values())[2]:,.1f} tCO₂e" if len(scopes) > 2 else "N/A",
            "Variance (Model - Reported)": f"{s3_variance:+,.1f} tCO₂e" if s3_variance is not None else "N/A",
            "Filing Source": filing_sec
        })
    st.table(pd.DataFrame(recon_data))

    with st.expander("🔍 DETAILED CORPORATE REGISTRY METADATA"):
        st.json(state.get("corporate_metadata", {}))
        st.json(state.get("brsr_reported_data", {}))

    st.subheader("DOCUMENTED EMISSION FACTOR REGISTRY & CITATIONS")
    st.json(ef_audit)
    st.subheader("DATA SOURCE & PROVENANCE AUDIT")
    st.json(dq)
    st.subheader("AGGREGATED ORGANIZATIONAL ACTIVITY (GROUPED BY ORG_ID & YEAR)")
    st.dataframe(org_raw_df, use_container_width=True)