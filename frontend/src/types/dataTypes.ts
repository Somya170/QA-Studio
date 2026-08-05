export interface Machine {
  machine_id: string;
  name: string;
  category: string;
  location: string;
  status: 'OPERATIONAL' | 'MAINTENANCE_DUE' | 'BREAKDOWN' | 'WARNING';
  health_score: number;
  installed_date: string;
  last_maintenance: string;
  next_scheduled_maintenance: string;
  total_downtime_hours: number;
  current_operator: string;
}

export interface MaintenanceLog {
  log_id: string;
  machine_id: string;
  date: string;
  issue_type: string;
  description: string;
  technician_notes: string;
  cost: number;
  downtime_hours: number;
  parts_replaced: string;
}

export interface EvidenceItem {
  row_index: number;
  source_file: string;
  data: Record<string, any>;
}

export interface GroundingAudit {
  is_grounded: boolean;
  confidence_score: number;
  sql_executed?: string;
  matched_row_count: number;
  matched_evidence: EvidenceItem[];
  reasoning_trace: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  execution_type: 'SQL_DETERMINISTIC' | 'SEMANTIC_TEXT' | 'HYBRID';
  audit: GroundingAudit;
  data_table?: Record<string, any>[];
  visualization_hint?: 'BAR_CHART' | 'LINE_CHART' | 'KPI_CARD' | 'TABLE';
}

export interface FleetSummary {
  total_machines: number;
  operational_count: number;
  maintenance_due_count: number;
  breakdown_count: number;
  warning_count: number;
  total_downtime_hours: number;
  total_maintenance_cost: number;
  average_health_score: number;
}

export interface AnalyticsOverview {
  fleet_summary: FleetSummary;
  downtime_by_category: { category: string; downtime_hours: number }[];
  cost_by_category: { category: string; cost: number }[];
  recent_maintenance_logs: MaintenanceLog[];
}
