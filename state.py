from typing import TypedDict, List, Dict, Any, Optional

class CarbonAgentState(TypedDict):
    org_name: str
    target_entity: str
    start_year: int
    end_year: int
    data_source_path: Optional[str]
    use_llm_narrative: bool

    # Agent 1: Ingestion
    org_activity_records: List[Dict[str, Any]]
    owid_benchmark_records: List[Dict[str, Any]]
    data_quality_report: Dict[str, Any]
    ingestion_status: str

    # Agent 2: Calculation
    computed_metrics: Dict[str, Any]
    scope_breakdown: Dict[str, float]
    emission_factors_audit: Dict[str, Any]
    annual_emissions_records: List[Dict[str, Any]]
    anomalies_detected: List[Dict[str, Any]]

    # Agent 3: ML Engine
    ml_evaluation_metrics: Dict[str, Any]
    forecast_records: List[Dict[str, Any]]

    # Agent 4 & 5: Reporting & Critic
    draft_report: str
    critic_approved: bool
    critic_feedback: Optional[str]
    faithfulness_score: float
    revision_count: int

    agent_logs: List[str]