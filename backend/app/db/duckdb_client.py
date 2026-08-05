import duckdb
from typing import List, Dict, Any
from app.config import DB_PATH

class DuckDBClient:
    def __init__(self, db_path=str(DB_PATH)):
        self.db_path = str(db_path)
        try:
            self.conn = duckdb.connect(self.db_path)
        except Exception:
            # Fallback to shared in-memory connection if file is locked by another process
            self.conn = duckdb.connect(":memory:")
        self._init_tables()

    def _init_tables(self):
        """Initializes tables if they do not exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                machine_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                category VARCHAR,
                location VARCHAR,
                status VARCHAR,
                health_score DOUBLE,
                installed_date VARCHAR,
                last_maintenance VARCHAR,
                next_scheduled_maintenance VARCHAR,
                total_downtime_hours DOUBLE,
                current_operator VARCHAR
            );
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_logs (
                log_id VARCHAR PRIMARY KEY,
                machine_id VARCHAR,
                date VARCHAR,
                issue_type VARCHAR,
                description VARCHAR,
                technician_notes VARCHAR,
                cost DOUBLE,
                downtime_hours DOUBLE,
                status VARCHAR,
                parts_replaced VARCHAR
            );
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS operator_schedules (
                schedule_id VARCHAR PRIMARY KEY,
                operator_id VARCHAR,
                operator_name VARCHAR,
                machine_id VARCHAR,
                shift VARCHAR,
                date VARCHAR,
                efficiency_rating DOUBLE,
                notes VARCHAR
            );
        """)

    def execute_query(self, query_str: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SQL query and returns results as list of dicts."""
        clean_query = query_str.strip()
        if not clean_query.upper().startswith("SELECT") and not clean_query.upper().startswith("WITH"):
            raise ValueError("Only SELECT or WITH queries are permitted for data safety.")

        cursor = self.conn.cursor()
        cursor.execute(clean_query, params)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def execute_raw(self, sql_str: str, params: tuple = ()):
        """Executes raw DDL or DML statement."""
        self.conn.execute(sql_str, params)

    def load_df(self, table_name: str, df):
        """Loads a pandas DataFrame into DuckDB table safely using CASCADE drop."""
        self.conn.register('temp_df', df)
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_df")
        self.conn.unregister('temp_df')

    def append_df(self, table_name: str, df):
        """Appends DataFrame rows to existing table, creates table if not exists."""
        self.conn.register('temp_df', df)
        # Check if table exists
        existing = self.list_tables()
        if table_name in existing:
            self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
        else:
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_df")
        self.conn.unregister('temp_df')

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        cursor = self.conn.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        return [{"column": row[0], "type": row[1]} for row in cursor.fetchall()]

    def list_tables(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]

# Singleton instance
db_client = DuckDBClient()
