import os
import json
from groq import Groq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from state import CarbonAgentState

load_dotenv()

def get_candidate_groq_models(api_key: str) -> list:
    """Returns an ordered list of verified text-generation LLMs available on this Groq key."""
    # Exact models confirmed working on your Groq account + top text models
    preferred_order = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "gemma2-9b-it",
        "allam-2-7b"
    ]
    blocked_keywords = [
        "orpheus", "canopylabs", "whisper", "guard", "tts", 
        "embed", "vision", "audio", "speech", "playai"
    ]
    try:
        client = Groq(api_key=api_key)
        models_response = client.models.list()
        available_ids = [m.id for m in models_response.data]

        candidates = [m for m in preferred_order if m in available_ids]
        for m in available_ids:
            if m not in candidates and not any(b in m.lower() for b in blocked_keywords):
                candidates.append(m)

        return candidates if candidates else preferred_order
    except Exception:
        return preferred_order


def reporting_agent(state: CarbonAgentState) -> dict:
    logs = state.get("agent_logs", [])
    revision = state.get("revision_count", 0)
    feedback = state.get("critic_feedback", None)

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in .env file!")

    candidate_models = get_candidate_groq_models(api_key)

    system_prompt = """You are an elite Chief Sustainability Officer (CSO) and ML Carbon Accounting AI Agent.
Generate a rigorous, quantitative, corporate-grade Carbon Footprint & ML Forecast Report in Markdown.

STRICT RULES:
1. ONLY use the exact numerical values provided in the JSON metrics. NEVER invent numbers.
2. You MUST include the exact latest CO2 value (end_co2_mt) and exact net_change_pct value verbatim in Section 1.
3. Structure the report with these exact 5 Markdown sections:
   - ## 1. Executive Summary & Carbon Trajectory
   - ## 2. GHG Protocol Scope Breakdown (Scope 1, 2 & 3 Proxies)
   - ## 3. Machine Learning Forecasting (2024–2030) & Anomaly Evaluation (F1, R², RMSE, Silhouette)
   - ## 4. Per-Capita & Energy Efficiency Benchmarking
   - ## 5. Automated Decarbonization Roadmap & Actionable Recommendations
4. Include a Markdown summary table of key metrics and ML evaluation scores (R², RMSE, F1-Score, Silhouette Score)."""

    user_payload = f"""
Target Entity / Region: {state['target_entity']}
Data Quality Notes: {json.dumps(state.get('data_quality_notes', []))}
Computed Quantitative Metrics: {json.dumps(state.get('computed_metrics', {}), indent=2)}
GHG Scope Breakdown (Latest Year): {json.dumps(state.get('scope_breakdown', {}), indent=2)}
Statistical Anomalies Detected: {json.dumps(state.get('anomalies_detected', []), indent=2)}
Machine Learning Model Evaluation Metrics (F1, R2, RMSE, Silhouette): {json.dumps(state.get('ml_evaluation_metrics', {}), indent=2)}
2024-2030 ML Forecast Trajectory: {json.dumps(state.get('forecast_records', []), indent=2)}
"""

    if feedback:
        user_payload += f"\n\n⚠️ CRITIC AGENT FEEDBACK FROM PREVIOUS DRAFT (MUST FIX):\n{feedback}"

    # Automatic Self-Healing Model Fallback Loop
    last_error = None
    for model_name in candidate_models:
        try:
            logs.append(f"✍️ [Reporting Agent] Generating Executive ESG & ML Report using '{model_name}' (Iteration #{revision + 1})...")
            llm = ChatGroq(model=model_name, temperature=0.2, api_key=api_key)
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_payload)
            ])
            logs.append(f"✅ [Reporting Agent] Draft ESG & ML report synthesized via '{model_name}'.")
            return {
                "draft_report": response.content,
                "revision_count": revision + 1,
                "agent_logs": logs
            }
        except Exception as e:
            last_error = e
            logs.append(f"⚠️ [Reporting Agent] Model '{model_name}' skipped ({str(e)[:60]}...). Trying next model...")
            continue

    raise RuntimeError(f"All candidate Groq models failed. Last error: {last_error}")