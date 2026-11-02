from typing import TypedDict, List, Dict, Any, Optional

class CarbonAgentState(TypedDict):
    # User Inputs
    target_entity: str
    start_year: int
    end_year: int
    
    # Agent 1: Ingestion
    raw_records: List[Dict[str, Any]]
    data_quality_notes: List[str]
    ingestion_status: str
    
    # Agent 2: Calculation & Statistical Metrics
    computed_metrics: Dict[str, Any]
    anomalies_detected: List[Dict[str, Any]]
    scope_breakdown: Dict[str, float]
    
    # Agent 3: Machine Learning & Evaluation Metrics (MUST BE IN STATE.PY!)
    ml_evaluation_metrics: Dict[str, Any]
    forecast_records: List[Dict[str, Any]]
    
    # Agent 4 & 5: Reporting & Critic
    draft_report: str
    critic_approved: bool
    critic_feedback: Optional[str]
    faithfulness_score: float
    revision_count: int
    
    # System Trace
    agent_logs: List[str]