import re
from typing import List, Dict, Any
from app.db.duckdb_client import db_client
from app.engine.profiler import get_active_profile

def perform_semantic_search(query: str, limit: int = 10, filter_document: str = None) -> List[Dict[str, Any]]:
    """
    Performs dynamic keyword search ranker across text/varchar columns in the active table.
    Uses SQL-based term matching counts to rank rows by relevance.
    """
    # 1. Discover target table
    tables = db_client.list_tables()
    if not tables:
        return []

    profile = get_active_profile()
    active_table = profile.get("table_name")
    
    if active_table and active_table in tables:
        target_table = active_table
    else:
        custom_tables = [t for t in tables if t not in ["machines", "maintenance_logs", "operator_schedules"]]
        target_table = custom_tables[0] if custom_tables else "maintenance_logs"
    
    if target_table not in tables:
        target_table = tables[0]

    # 2. Retrieve columns and filter for text types
    try:
        cols = db_client.get_table_schema(target_table)
    except Exception:
        return []
        
    text_cols = [c["column"] for c in cols if "varchar" in c["type"].lower() or "string" in c["type"].lower()]
    if not text_cols:
        text_cols = [c["column"] for c in cols] # Fallback to all columns if no text type detected

    # Clean query terms (strip punctuation)
    query_clean = re.sub(r'[^\w\s]', ' ', query)
    terms = [t.strip().lower() for t in query_clean.split() if len(t.strip()) > 2]
    # Filter out common stopwords
    stopwords = {"what", "how", "fix", "why", "the", "and", "for", "with", "from", "show", "list", "tell", "give"}
    terms = [t for t in terms if t not in stopwords]
    if not terms:
        terms = [query.lower()]

    # 3. Build dynamic SQL search ranker
    score_components = []
    where_conditions = []
    
    for term in terms:
        term_escaped = term.replace("'", "''")
        col_checks = [f"CASE WHEN LOWER({tc}) LIKE '%{term_escaped}%' THEN 1 ELSE 0 END" for tc in text_cols]
        score_components.append(f"({' + '.join(col_checks)})")
        
        col_conds = [f"LOWER({tc}) LIKE '%{term_escaped}%'" for tc in text_cols]
        where_conditions.append(f"({' OR '.join(col_conds)})")

    score_select = " + ".join(score_components)
    where_clause = " OR ".join(where_conditions)

    # Add document filter if specified
    if filter_document and target_table == 'documents':
        where_clause = f"(filename = '{filter_document}') AND ({where_clause})"

    sql = f"""
        SELECT *, ({score_select}) as match_score
        FROM {target_table}
        WHERE {where_clause}
        ORDER BY match_score DESC
        LIMIT {limit};
    """

    try:
        results = db_client.execute_query(sql)
        # Remove match_score from results to prevent pollution of grounding auditor evidence
        for r in results:
            r.pop("match_score", None)
        return results
    except Exception as e:
        print("SQL Search Ranker Failed:", e)
        # Final fallback query
        try:
            return db_client.execute_query(f"SELECT * FROM {target_table} LIMIT {limit};")
        except Exception:
            return []
