import re
import json
from typing import Dict, Any, List, Tuple
from app.db.duckdb_client import db_client
from app.llm.cloud_provider import cloud_llm

def get_all_tables_with_schemas() -> List[Dict[str, Any]]:
    tables = db_client.list_tables()
    schemas = []
    for t in tables:
        cols = db_client.get_table_schema(t)
        schemas.append({
            "table_name": t,
            "columns": {c["column"].lower(): c["type"] for c in cols},
            "raw_columns": [c["column"] for c in cols]
        })
    return schemas

def build_heuristic_sql(query: str, table_schemas: List[Dict[str, Any]], filter_machine_id: str = None, filter_category: str = None) -> Tuple[str, str]:
    """Fallback heuristic SQL generator when LLM is unavailable."""
    q_lower = query.lower()
    mac_match = re.search(r'mac-?(\d+)', q_lower)
    target_id = f"MAC-{int(mac_match.group(1)):04d}" if mac_match else (filter_machine_id or None)
    
    best_table = None
    best_score = -1
    
    for schema_info in table_schemas:
        t_name = schema_info["table_name"].lower()
        cols = schema_info["columns"]
        score = 0
        
        # Domain routing boosts based on entity prefixes
        if "mac-" in q_lower or "machine" in q_lower or "downtime" in q_lower:
            if "machine" in t_name or "maintenance" in t_name:
                score += 50
        if "emp-" in q_lower or "employee" in q_lower or "attendance" in q_lower:
            if "employee" in t_name or "attendance" in t_name:
                score += 50
        if "flt-" in q_lower or "vehicle" in q_lower or "fleet" in q_lower:
            if "fleet" in t_name or "vehicle" in t_name:
                score += 50
        if "inv-" in q_lower or "sales" in q_lower or "inventory" in q_lower or "unit_price" in q_lower:
            if "sales" in t_name or "inventory" in t_name:
                score += 50

        # General keyword matching score
        for col_name in cols:
            if col_name in q_lower:
                score += 5
            if "downtime" in q_lower and "downtime" in col_name:
                score += 10
            if "cost" in q_lower and ("cost" in col_name or "price" in col_name):
                score += 10
            if any(k in q_lower for k in ["operator", "worker", "technician", "shift", "timing"]) and ("operator" in col_name or "technician" in col_name or "shift" in col_name or "name" in col_name):
                score += 10
                
        if score > best_score:
            best_score = score
            best_table = schema_info

    if not best_table:
        best_table = table_schemas[0]

    t_name = best_table["table_name"]
    cols = best_table["columns"]
    raw_cols = best_table["raw_columns"]

    def find_col(candidates: List[str]) -> str:
        for cand in candidates:
            for c in raw_cols:
                if cand.lower() in c.lower():
                    return c
        return None

    col_mac_id = find_col(["machine_id", "machine", "id", "equipment_id", "vehicle_id", "item_id", "employee_id"])
    col_name = find_col(["name", "machine_name", "title", "product_name", "employee_name", "model"])
    col_category = find_col(["category", "type", "group", "department"])
    col_downtime = find_col(["downtime_hours", "downtime", "hours_lost", "hours_worked"])
    col_cost = find_col(["cost", "repair_cost", "maintenance_cost", "price", "unit_price"])
    col_operator = find_col(["operator_name", "operator", "technician", "worker", "driver_assigned"])

    viz_hint = "TABLE"
    
    # 1. Direct Entity ID filter (Highest precedence)
    entity_match = re.search(r'(mac|emp|flt|inv)-?(\d+)', q_lower)
    if entity_match and col_mac_id:
        prefix = entity_match.group(1).upper()
        num = int(entity_match.group(2))
        full_id = f"{prefix}-{num}"
        # Also try matching matching partial numeric string in case prefix is omitted
        sql = f"SELECT * FROM {t_name} WHERE LOWER({col_mac_id}) LIKE '%{full_id.lower()}%' OR LOWER({col_mac_id}) LIKE '%{prefix}{num}%' OR {col_mac_id} LIKE '%{num}%' LIMIT 20;"
    
    # 2. Operator filtering (e.g. operated by Ananya Roy)
    elif any(k in q_lower for k in ["operator", "who", "worker", "operated", "driver", "assigned"]) and col_operator:
        query_words = [w for w in re.split(r'\W+', q_lower) if len(w) > 2 and w not in ["show", "list", "what", "which", "machine", "data", "file", "tell", "give", "and", "the", "for", "with", "notes", "timing", "operator", "operated", "who", "worker", "issue", "downtime", "driver", "assigned"]]
        if query_words:
            conditions = [f"LOWER({col_operator}) LIKE '%{w}%'" for w in query_words]
            sql = f"SELECT * FROM {t_name} WHERE {' OR '.join(conditions)} LIMIT 20;"
        else:
            sql = f"SELECT * FROM {t_name} WHERE {col_operator} IS NOT NULL LIMIT 20;"

    # 3. Downtime / Hours Worked Aggregation (Only if aggregation keywords are explicitly asked)
    elif ("downtime" in q_lower or "hours" in q_lower) and col_downtime and any(k in q_lower for k in ["highest", "max", "most", "total", "sum", "average", "avg", "worst", "least", "compare"]):
        select_cols = [c for c in [col_mac_id, col_name, col_category] if c]
        select_str = ", ".join(select_cols) + ", " if select_cols else ""
        group_str = ", ".join(select_cols) if select_cols else raw_cols[0]
        sql = f"SELECT {select_str} ROUND(SUM({col_downtime}), 1) AS total_downtime_hours FROM {t_name} GROUP BY {group_str} ORDER BY total_downtime_hours DESC LIMIT 10;"
        viz_hint = "BAR_CHART"
        
    # 4. Cost / Price Aggregation (Only if aggregation keywords are explicitly asked)
    elif ("cost" in q_lower or "spend" in q_lower or "price" in q_lower) and col_cost and any(k in q_lower for k in ["highest", "max", "most", "total", "sum", "average", "avg", "worst", "least", "compare"]):
        select_cols = [c for c in [col_mac_id, col_name, col_category] if c]
        select_str = ", ".join(select_cols) + ", " if select_cols else ""
        group_str = ", ".join(select_cols) if select_cols else raw_cols[0]
        sql = f"SELECT {select_str} ROUND(SUM({col_cost}), 2) AS total_maintenance_cost FROM {t_name} GROUP BY {group_str} ORDER BY total_maintenance_cost DESC LIMIT 10;"
        viz_hint = "BAR_CHART"
        
    # 5. General text keyword search
    else:
        text_cols = [c for c, dtype in cols.items() if "varchar" in dtype.lower() or "string" in dtype.lower()]
        stop_words = ["show", "list", "what", "which", "machine", "data", "file", "tell", "give", "and", "the", "for", "with", "notes", "timing"]
        query_words = [w for w in re.split(r'\W+', q_lower) if len(w) > 2 and w not in stop_words]
        if query_words and text_cols:
            where_conditions = [f"LOWER({tc}) LIKE '%{w}%'" for w in query_words for tc in text_cols]
            sql = f"SELECT * FROM {t_name} WHERE " + " OR ".join(where_conditions) + " LIMIT 20;"
        else:
            sql = f"SELECT * FROM {t_name} LIMIT 20;"

    return sql, viz_hint

def generate_and_execute_sql(query: str, filter_machine_id: str = None, filter_category: str = None) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Translates Natural Language queries into 100% exact DuckDB SQL
    using Gemini/Groq AI if initialized, with heuristic backup.
    """
    table_schemas = get_all_tables_with_schemas()
    if not table_schemas:
        return "", [], "TABLE"

    custom_tables = [t["table_name"] for t in table_schemas if t["table_name"] not in ["machines", "maintenance_logs", "operator_schedules"]]

    # Try LLM SQL Generation if initialized
    if cloud_llm.initialized:
        try:
            schema_json = json.dumps(table_schemas, indent=2)
            
            instruction_custom = ""
            if custom_tables:
                instruction_custom = (
                    f"\n\nCRITICAL NOTE: The user has uploaded custom tables: {', '.join(custom_tables)}.\n"
                    "Select the correct table name from the list based on the entity details in the user query:\n"
                    "- If the query contains 'MAC-XXXX' identifiers, search the relevant machine table (e.g. 'sample_test_machines' or 'machines').\n"
                    "- If the query contains 'EMP-XXXX' or asks about employee check-ins, search 'sample_employee_attendance'.\n"
                    "- If the query contains 'FLT-XXXX' or asks about vehicles/mileage, search 'sample_fleet_vehicles'.\n"
                    "- If the query contains 'INV-XXXX' or asks about sales/price, search 'sample_sales_inventory'.\n"
                    "Do NOT query a table that does not contain the required entity IDs."
                )

            system_prompt = (
                "You are an expert SQL Generator for DuckDB.\n"
                "Given the table schemas (JSON format) and a user query, generate ONLY the raw SQL query to get the exact data needed.\n"
                "Rules:\n"
                "1. Output ONLY the raw SQL string. Do not include markdown code block backticks (like ```sql or ```).\n"
                "2. Ensure queries are SELECT-only.\n"
                "3. Perform case-insensitive searches using LOWER() or ILIKE for text matching.\n"
                "4. For lookup, details, or filtering queries about a specific operator, machine, or record, ALWAYS use 'SELECT *' "
                "instead of projecting specific column names. This ensures the full row context is returned for verification.\n"
                "5. Remember: 'machine_id' contains codes like 'MAC-5001', 'MAC-5004', 'MAC-5007'. Do NOT search for 'MAC-XXXX' "
                "in the 'name' column; always filter on the 'machine_id' column for code identifiers.\n"
                "6. Prefer LIKE/ILIKE partial matching (e.g. LOWER(name) LIKE '%cnc%') instead of exact equal (=) comparison for text columns.\n"
                "7. Limit output rows to 20 for lists unless it's a SUM/AVG/COUNT aggregation.\n"
                "8. Only use tables that exist in the provided schema."
                f"{instruction_custom}"
            )
            prompt = f"Table Schemas:\n{schema_json}\n\nUser Question:\n{query}"
            
            sql = cloud_llm.generate(prompt, system_prompt=system_prompt)
            sql = sql.replace("```sql", "").replace("```", "").strip()
            
            results = db_client.execute_query(sql)
            
            q_lower = query.lower()
            viz_hint = "TABLE"
            if "downtime" in q_lower or "cost" in q_lower or "spend" in q_lower:
                if "highest" in q_lower or "max" in q_lower or "total" in q_lower or "sum" in q_lower:
                    viz_hint = "BAR_CHART"
            elif "breakdown" in q_lower or "status" in q_lower:
                viz_hint = "KPI_CARD"
                
            return sql, results, viz_hint
        except Exception as err:
            print("Gemini Text-to-SQL Fallback triggered due to:", err)

    # Heuristic Fallback if Gemini not set up or query fails
    sql, viz_hint = build_heuristic_sql(query, table_schemas, filter_machine_id, filter_category)
    try:
        results = db_client.execute_query(sql)
    except Exception:
        sql = f"SELECT * FROM {table_schemas[0]['table_name']} LIMIT 20;"
        results = db_client.execute_query(sql)

    return sql, results, viz_hint
