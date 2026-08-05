import re
from typing import Dict, Any

def classify_query(query: str) -> Dict[str, Any]:
    """Classifies user intent: SQL_DETERMINISTIC, SEMANTIC_TEXT, or HYBRID."""
    q_lower = query.lower()

    sql_keywords = [
        "highest", "lowest", "max", "min", "total", "sum", "average", "avg", "count",
        "downtime", "cost", "how many", "which machine", "list", "top", "schedule",
        "shift", "operator", "category", "status", "breakdown", "history", "logs",
        "mac-", "log-", "sch-"
    ]

    semantic_keywords = [
        "why", "technician notes", "reason", "description", "issue", "notes", "report", "fault explanation"
    ]

    is_sql = any(k in q_lower for k in sql_keywords)
    is_semantic = any(k in q_lower for k in semantic_keywords)

    if is_sql and is_semantic:
        execution_type = "HYBRID"
    elif is_semantic and not is_sql:
        execution_type = "SEMANTIC_TEXT"
    else:
        execution_type = "SQL_DETERMINISTIC"

    return {
        "execution_type": execution_type,
        "query": query
    }
