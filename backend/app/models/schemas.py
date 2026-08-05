from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question about machine logs, schedules, or analytics")
    filter_machine_id: Optional[str] = None
    filter_category: Optional[str] = None
    filter_document: Optional[str] = None

class EvidenceItem(BaseModel):
    row_index: int
    source_file: str
    data: Dict[str, Any]

class GroundingAudit(BaseModel):
    is_grounded: bool
    confidence_score: float = Field(..., ge=0.0, le=100.0)
    sql_executed: Optional[str] = None
    matched_row_count: int
    matched_evidence: List[EvidenceItem] = []
    reasoning_trace: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    execution_type: str  # "SQL_DETERMINISTIC", "SEMANTIC_TEXT", or "HYBRID"
    audit: GroundingAudit
    data_table: Optional[List[Dict[str, Any]]] = None
    visualization_hint: Optional[str] = None  # "BAR_CHART", "LINE_CHART", "KPI_CARD", "TABLE"

class IngestResponse(BaseModel):
    filename: str
    status: str
    rows_inserted: int
    columns_detected: List[str]
    table_name: str

class MachineStatus(BaseModel):
    machine_id: str
    name: str
    category: str
    location: str
    status: str  # "OPERATIONAL", "MAINTENANCE_DUE", "BREAKDOWN", "WARNING"
    health_score: float
    last_maintenance: str
    next_scheduled_maintenance: str
    total_downtime_hours: float
    current_operator: str

class FleetSummary(BaseModel):
    total_machines: int
    operational_count: int
    maintenance_due_count: int
    breakdown_count: int
    warning_count: int
    total_downtime_hours: float
    total_maintenance_cost: float
    average_health_score: float

class AnalyticsOverview(BaseModel):
    fleet_summary: FleetSummary
    downtime_by_category: List[Dict[str, Any]]
    cost_by_category: List[Dict[str, Any]]
    recent_maintenance_logs: List[Dict[str, Any]]
