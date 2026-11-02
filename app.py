import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from main import run_pipeline

load_dotenv()

st.set_page_config(page_title="CarbonTrace | Multi-Agent ML & ESG Intelligence", page_icon="🌍", layout="wide")

st.title("🌍 CarbonTrace — Autonomous Multi-Agent Carbon & ML Intelligence")
st.caption("5-Agent Cyclic LangGraph Pipeline | Polynomial Ridge Forecasting | Isolation Forest Anomalies | K-Means Clustering")

with st.sidebar:
    st.header("⚙️ Pipeline Controls")
    api_key_input = st.text_input("Groq API Key (Optional if set in .env)", type="password", value=os.getenv("GROQ_API_KEY", ""))
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input

    entity = st.selectbox(
        "Select Target Entity / Region",
        ["India", "United States", "China", "European Union (27)", "United Kingdom", "Germany", "Japan", "World"],
        index=0
    )
    year_range = st.slider("Select Evaluation Window", min_value=1990, max_value=2023, value=(2000, 2023))
    run_btn = st.button("🚀 Execute 5-Agent ML Pipeline", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🧠 5-Agent Cyclic Topology")
    st.markdown("""
    1. **Ingestion Agent**: Live OWID & Linear Imputation
    2. **Calculation Agent**: GHG Scopes, CAGR & Z-Score
    3. **ML Engine Agent**: Ridge Forecast ($R^2$, RMSE), Isolation Forest (F1-Score) & K-Means (Silhouette)
    4. **Reporting Agent**: Executive ESG Synthesizer
    5. **Critic Agent**: Hallucination Guard & Faithfulness Score
    """)

if run_btn:
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ Please add your `GROQ_API_KEY` in `.env`!")
        st.stop()

    with st.spinner(f"🤖 Orchestrating 5 autonomous agents & training ML models for {entity}..."):
        state = run_pipeline(entity=entity, start_year=year_range[0], end_year=year_range[1])

    if state["ingestion_status"] != "SUCCESS":
        st.error(f"Pipeline Failed: {state['data_quality_notes']}")
        st.stop()

    metrics = state["computed_metrics"]
    ml = state["ml_evaluation_metrics"]
    df = pd.DataFrame(state["raw_records"])
    forecast_df = pd.DataFrame(state["forecast_records"])
    anomalies = state["anomalies_detected"]
    scopes = state["scope_breakdown"]

    # Row 1: Carbon KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest Annual CO₂", f"{metrics['end_co2_mt']:,.2f} Mt", f"{metrics['net_change_pct']:+.2f}% Net")
    c2.metric("2030 ML Projected CO₂", f"{ml.get('predicted_2030_co2_mt', 0):,.2f} Mt", f"CAGR: {metrics['cagr_pct']:+.2f}%/yr")
    c3.metric("Anomaly Detection F1-Score", f"{ml.get('anomaly_f1_score', 0):.3f}", f"Precision: {ml.get('anomaly_precision', 0):.2f} | Recall: {ml.get('anomaly_recall', 0):.2f}")
    c4.metric("Regression R² / MAPE", f"R² = {ml.get('r2_score', 0):.3f}", f"MAPE: {ml.get('mape_pct', 0):.2f}% | Faithfulness: {state['faithfulness_score']}%")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 ML Forecasting & Evaluation Metrics",
        "📊 GHG Scopes & Anomaly Telemetry",
        "📄 Generated ESG & ML Report",
        "🤖 Live Agent Trace & Raw Data"
    ])

    with tab1:
        st.subheader(f"📈 Historical Trajectory & 2024–2030 ML Forecast with 95% Confidence Band ({entity})")
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=df["year"], y=df["co2"], mode="lines+markers",
            name="Historical CO₂ (Mt)", line=dict(color="#00CC96", width=3)
        ))
        if not forecast_df.empty:
            fig_fc.add_trace(go.Scatter(
                x=forecast_df["year"], y=forecast_df["predicted_co2_mt"],
                mode="lines+markers", name="ML Forecast (2024–2030)",
                line=dict(color="#636EFA", width=3, dash="dash")
            ))
            fig_fc.add_trace(go.Scatter(
                x=list(forecast_df["year"]) + list(forecast_df["year"])[::-1],
                y=list(forecast_df["ci_upper_mt"]) + list(forecast_df["ci_lower_mt"])[::-1],
                fill="toself", fillcolor="rgba(99, 110, 250, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% Confidence Interval"
            ))
        if anomalies:
            anom_df = pd.DataFrame(anomalies)
            fig_fc.add_trace(go.Scatter(
                x=anom_df["year"], y=anom_df["co2_mt"], mode="markers",
                name="Detected Anomaly", marker=dict(color="#EF553B", size=14, symbol="star")
            ))
        fig_fc.update_layout(height=430, xaxis_title="Year", yaxis_title="Million Tonnes CO₂ (Mt)")
        st.plotly_chart(fig_fc, use_container_width=True)

        st.subheader("🔬 Quantitative AI/ML Model Evaluation Benchmarks")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("#### 1. Time-Series Regression")
            st.write(f"**Model:** `{ml.get('forecast_model')}`")
            st.write(f"- **$R^2$ Score (Goodness of Fit):** `{ml.get('r2_score')}`")
            st.write(f"- **RMSE:** `{ml.get('rmse_mt')} Mt`")
            st.write(f"- **MAE:** `{ml.get('mae_mt')} Mt`")
            st.write(f"- **MAPE (Error %):** `{ml.get('mape_pct')}%`")
        with m2:
            st.markdown("#### 2. Anomaly Classification")
            st.write(f"**Model:** `{ml.get('anomaly_model')}`")
            st.write(f"- **F1-Score:** `{ml.get('anomaly_f1_score')}`")
            st.write(f"- **Precision:** `{ml.get('anomaly_precision')}`")
            st.write(f"- **Recall:** `{ml.get('anomaly_recall')}`")
        with m3:
            st.markdown("#### 3. Regime Clustering & LLM Audit")
            st.write(f"**Model:** `{ml.get('clustering_model')}`")
            st.write(f"- **Silhouette Score:** `{ml.get('silhouette_score')}`")
            st.write(f"- **LLM Grounding Faithfulness:** `{state['faithfulness_score']}%`")
            st.write(f"- **Self-Reflection Revisions:** `{state['revision_count']}`")

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("GHG Protocol Corporate Scope Proxies")
            scope_df = pd.DataFrame({"Scope Category": list(scopes.keys()), "Emissions (Mt)": list(scopes.values())})
            fig_pie = px.pie(scope_df, names="Scope Category", values="Emissions (Mt)", hole=0.45)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_b:
            st.subheader("⚠️ Statistical & Isolation Forest Anomaly Log")
            if anomalies:
                st.dataframe(pd.DataFrame(anomalies), use_container_width=True)
            st.subheader("🔮 2024–2030 Forecast Table")
            st.dataframe(forecast_df, use_container_width=True)

    with tab3:
        st.download_button(
            label="📥 Download Official ESG & ML Report (.md)",
            data=state["draft_report"],
            file_name=f"CarbonTrace_ML_Report_{entity}_{year_range[0]}_{year_range[1]}.md",
            mime="text/markdown",
            type="primary"
        )
        st.markdown(state["draft_report"])

    with tab4:
        for log in state["agent_logs"]:
            st.code(log, language="text")
        st.dataframe(df, use_container_width=True)
else:
    st.info("👈 Click **Execute 5-Agent ML Pipeline** in the sidebar to train models, compute F1/R²/RMSE metrics, and generate your report.")