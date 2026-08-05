from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.db.duckdb_client import db_client
from app.models.schemas import AnalyticsOverview, FleetSummary

router = APIRouter()

@router.get("/machines")
def get_machines(
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Retrieves list of machines with filtering and pagination."""
    where_clauses = []
    if category:
        where_clauses.append(f"category = '{category}'")
    if status:
        where_clauses.append(f"status = '{status}'")
    if search:
        where_clauses.append(f"(LOWER(machine_id) LIKE '%{search.lower()}%' OR LOWER(name) LIKE '%{search.lower()}%')")

    where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    sql = f"""
        SELECT machine_id, name, category, location, status, health_score,
               installed_date, last_maintenance, next_scheduled_maintenance,
               total_downtime_hours, current_operator
        FROM machines
        {where_str}
        ORDER BY machine_id ASC
        LIMIT {limit} OFFSET {offset};
    """
    
    count_sql = f"SELECT COUNT(*) as total FROM machines {where_str};"
    
    try:
        rows = db_client.execute_query(sql)
        total_res = db_client.execute_query(count_sql)
        total_count = total_res[0]["total"] if total_res else len(rows)

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "machines": rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Machines Fetch Error: {str(e)}")

@router.get("/analytics")
def get_fleet_analytics():
    """Returns aggregated KPI summary and chart data for fleet or custom analytics."""
    try:
        from app.engine.profiler import get_active_profile
        profile = get_active_profile()
        table_name = profile.get("table_name")

        # Dynamic Custom Table Analytics
        if table_name and table_name != "machines":
            cols = db_client.get_table_schema(table_name)
            col_names = [c["column"] for c in cols]
            
            def find_col(candidates: list):
                for cand in candidates:
                    for c in col_names:
                        if cand.lower() in c.lower():
                            return c
                return None

            col_id = find_col(["id", "code", "number"]) or col_names[0]
            col_name = find_col(["name", "title", "model", "product"]) or col_names[0]
            col_cat = find_col(["category", "type", "dept", "department", "group"]) or col_names[0]
            col_date = find_col(["date", "time", "day"]) or col_names[0]
            
            # Numeric columns
            num_cols = [c["column"] for c in cols if "int" in c["type"].lower() or "double" in c["type"].lower() or "float" in c["type"].lower() or "decimal" in c["type"].lower()]
            col_val1 = num_cols[0] if len(num_cols) > 0 else None
            col_val2 = num_cols[1] if len(num_cols) > 1 else None

            total_rows = db_client.execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")[0]["cnt"]
            
            sum_val1 = 0.0
            avg_val1 = 0.0
            if col_val1:
                res = db_client.execute_query(f"SELECT SUM({col_val1}) as s, AVG({col_val1}) as a FROM {table_name}")[0]
                sum_val1 = float(res["s"] or 0)
                avg_val1 = float(res["a"] or 0)
                
            sum_val2 = 0.0
            if col_val2:
                sum_val2 = float(db_client.execute_query(f"SELECT SUM({col_val2}) as s FROM {table_name}")[0]["s"] or 0)

            # Group charts data
            downtime_by_cat = []
            cost_by_cat = []
            
            if col_cat:
                val_col = col_val2 or col_val1
                if val_col:
                    downtime_sql = f"SELECT {col_cat} as category, ROUND(SUM({val_col}), 1) as downtime_hours FROM {table_name} GROUP BY {col_cat} ORDER BY downtime_hours DESC"
                    downtime_by_cat = db_client.execute_query(downtime_sql)
                    
                val_cost_col = col_val1
                if val_cost_col:
                    cost_sql = f"SELECT {col_cat} as category, ROUND(SUM({val_cost_col}), 2) as cost FROM {table_name} GROUP BY {col_cat} ORDER BY cost DESC"
                    cost_by_cat = db_client.execute_query(cost_sql)

            # Recent records
            records_sql = f"SELECT * FROM {table_name} LIMIT 10"
            raw_records = db_client.execute_query(records_sql)
            recent_logs = []
            
            for idx, r in enumerate(raw_records):
                recent_logs.append({
                    "log_id": str(r.get(col_id) or f"REC-{idx+1}"),
                    "machine_id": str(r.get(col_name) or "Record"),
                    "date": str(r.get(col_date) or "2026-07-22"),
                    "issue_type": str(r.get(col_cat) or "General"),
                    "cost": float(r.get(col_val1) or 0.0) if col_val1 else 0.0,
                    "downtime_hours": float(r.get(col_val2) or 0.0) if col_val2 else 0.0,
                    "parts_replaced": f"Custom mapping for {table_name}"
                })

            fleet_summary = FleetSummary(
                total_machines=int(total_rows),
                operational_count=int(total_rows),
                maintenance_due_count=0,
                breakdown_count=0,
                warning_count=0,
                total_downtime_hours=sum_val2 if col_val2 else sum_val1,
                total_maintenance_cost=sum_val1,
                average_health_score=round(avg_val1, 1)
            )

            return AnalyticsOverview(
                fleet_summary=fleet_summary,
                downtime_by_category=downtime_by_cat,
                cost_by_category=cost_by_cat,
                recent_maintenance_logs=recent_logs
            )

        # Standard 1,000 Fleet Analytics
        summary_sql = """
            SELECT 
                COUNT(*) AS total_machines,
                SUM(CASE WHEN status = 'OPERATIONAL' THEN 1 ELSE 0 END) AS operational_count,
                SUM(CASE WHEN status = 'MAINTENANCE_DUE' THEN 1 ELSE 0 END) AS maintenance_due_count,
                SUM(CASE WHEN status = 'BREAKDOWN' THEN 1 ELSE 0 END) AS breakdown_count,
                SUM(CASE WHEN status = 'WARNING' THEN 1 ELSE 0 END) AS warning_count,
                ROUND(SUM(total_downtime_hours), 1) AS total_downtime_hours,
                ROUND(AVG(health_score), 1) AS average_health_score
            FROM machines;
        """
        summary_res = db_client.execute_query(summary_sql)[0]

        cost_sql = "SELECT ROUND(SUM(cost), 2) AS total_cost FROM maintenance_logs;"
        cost_res = db_client.execute_query(cost_sql)
        total_cost = cost_res[0]["total_cost"] if cost_res and cost_res[0]["total_cost"] else 0.0

        fleet_summary = FleetSummary(
            total_machines=summary_res["total_machines"] or 0,
            operational_count=summary_res["operational_count"] or 0,
            maintenance_due_count=summary_res["maintenance_due_count"] or 0,
            breakdown_count=summary_res["breakdown_count"] or 0,
            warning_count=summary_res["warning_count"] or 0,
            total_downtime_hours=summary_res["total_downtime_hours"] or 0.0,
            total_maintenance_cost=total_cost,
            average_health_score=summary_res["average_health_score"] or 0.0
        )

        downtime_sql = """
            SELECT m.category, ROUND(SUM(l.downtime_hours), 1) AS downtime_hours
            FROM machines m
            JOIN maintenance_logs l ON m.machine_id = l.machine_id
            GROUP BY m.category
            ORDER BY downtime_hours DESC;
        """
        downtime_by_cat = db_client.execute_query(downtime_sql)

        cost_cat_sql = """
            SELECT m.category, ROUND(SUM(l.cost), 2) AS cost
            FROM machines m
            JOIN maintenance_logs l ON m.machine_id = l.machine_id
            GROUP BY m.category
            ORDER BY cost DESC;
        """
        cost_by_cat = db_client.execute_query(cost_cat_sql)

        recent_sql = """
            SELECT log_id, machine_id, date, issue_type, cost, downtime_hours, parts_replaced
            FROM maintenance_logs
            ORDER BY date DESC
            LIMIT 10;
        """
        recent_logs = db_client.execute_query(recent_sql)

        return AnalyticsOverview(
            fleet_summary=fleet_summary,
            downtime_by_category=downtime_by_cat,
            cost_by_category=cost_by_cat,
            recent_maintenance_logs=recent_logs
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics Fetch Error: {str(e)}")
