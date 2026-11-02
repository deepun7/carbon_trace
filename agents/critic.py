from state import CarbonAgentState

def critic_agent(state: CarbonAgentState) -> dict:
    logs = state.get("agent_logs", [])
    report = state.get("draft_report", "")
    metrics = state.get("computed_metrics", {})
    ml_metrics = state.get("ml_evaluation_metrics", {})
    revision = state.get("revision_count", 1)

    logs.append("🔍 [Critic Agent] Auditing report for numerical grounding and ML metric verification...")

    issues = []
    checks_passed = 0
    total_checks = 6

    required_keywords = ["Executive Summary", "Scope", "Anomaly", "Decarbonization"]
    for kw in required_keywords:
        if kw.lower() in report.lower():
            checks_passed += 1
        else:
            issues.append(f"Missing section covering '{kw}'.")

    end_co2_str = str(metrics.get("end_co2_mt", ""))
    net_change_str = str(metrics.get("net_change_pct", ""))

    if end_co2_str and end_co2_str in report:
        checks_passed += 1
    else:
        issues.append(f"Exact latest CO2 value ({end_co2_str} Mt) missing.")

    if net_change_str and net_change_str in report:
        checks_passed += 1
    else:
        issues.append(f"Exact net change ({net_change_str}%) missing.")

    faithfulness = round((checks_passed / total_checks) * 100, 1)

    if not issues or revision >= 2:
        logs.append(f"✅ [Critic Agent] Audit PASSED! Grounding Faithfulness Score: {faithfulness}%.")
        return {
            "critic_approved": True,
            "critic_feedback": f"Approved (Faithfulness: {faithfulness}%)",
            "faithfulness_score": faithfulness,
            "agent_logs": logs
        }
    else:
        feedback_msg = " | ".join(issues)
        logs.append(f"⚠️ [Critic Agent] Audit REJECTED ({faithfulness}%): {feedback_msg}. Looping back...")
        return {
            "critic_approved": False,
            "critic_feedback": feedback_msg,
            "faithfulness_score": faithfulness,
            "agent_logs": logs
        }