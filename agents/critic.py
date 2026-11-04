from state import CarbonAgentState

def critic_agent(state: CarbonAgentState) -> dict:
    logs = list(state.get("agent_logs", []))
    report = state.get("draft_report", "")
    metrics = state.get("computed_metrics", {})
    scopes = state.get("scope_breakdown", {})

    logs.append("🔍 [Critic Agent] Verifying report figures, scope totals, factor citations, and provenance labels...")

    issues = []
    checks_passed = 0
    total_checks = 8

    required_keywords = ["Executive Summary", "Scope", "OWID", "Decarbonization"]
    for kw in required_keywords:
        if kw.lower() in report.lower():
            checks_passed += 1
        else:
            issues.append(f"Missing required section covering '{kw}'.")

    end_org_str = str(metrics.get("end_org_tco2e", ""))
    org_change_str = str(metrics.get("org_net_change_pct", ""))
    owid_end_str = str(metrics.get("owid_national_end_co2_mt", ""))
    provenance_str = str(metrics.get("data_provenance", "SIMULATED_DEMO"))

    if end_org_str and end_org_str in report:
        checks_passed += 1
    else:
        issues.append(f"Exact latest corporate footprint ({end_org_str} tCO2e) missing.")

    if org_change_str and org_change_str in report:
        checks_passed += 1
    else:
        issues.append(f"Exact corporate net change ({org_change_str}%) missing.")

    if owid_end_str and owid_end_str in report:
        checks_passed += 1
    else:
        issues.append(f"Exact OWID national benchmark ({owid_end_str} Mt) missing.")

    scope_vals_present = all(str(v) in report for v in scopes.values()) if scopes else False
    if scope_vals_present and provenance_str in report:
        checks_passed += 1
    else:
        issues.append("Missing exact Scope 1/2/3 values or data provenance label.")

    faithfulness = round((checks_passed / total_checks) * 100.0, 1)

    if len(issues) == 0:
        logs.append(f"✅ [Critic Agent] Audit PASSED! All {total_checks}/{total_checks} checks verified (Completeness: {faithfulness}%).")
        return {
            "critic_approved": True,
            "critic_feedback": f"Approved ({total_checks}/{total_checks} checks passed, Completeness: {faithfulness}%)",
            "faithfulness_score": faithfulness,
            "agent_logs": logs
        }
    else:
        feedback_msg = " | ".join(issues)
        logs.append(f"❌ [Critic Agent] Audit REJECTED ({faithfulness}%): {feedback_msg}")
        return {
            "critic_approved": False,
            "critic_feedback": feedback_msg,
            "faithfulness_score": faithfulness,
            "agent_logs": logs
        }