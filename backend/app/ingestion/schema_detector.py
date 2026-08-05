import pandas as pd
from typing import Dict, Any, List

def detect_schema_and_relationships(df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
    """Detects column types, primary key candidates, and relationships."""
    schema = {}
    primary_key_candidate = None

    for col in df.columns:
        dtype = str(df[col].dtype)
        if "int" in dtype or "float" in dtype:
            sql_type = "DOUBLE"
        elif "datetime" in dtype:
            sql_type = "TIMESTAMP"
        else:
            sql_type = "VARCHAR"

        schema[col] = sql_type

        # Check for ID candidates
        if ("id" in col.lower() or "code" in col.lower()) and df[col].nunique() == len(df):
            if not primary_key_candidate:
                primary_key_candidate = col

    return {
        "table_name": table_name,
        "columns": schema,
        "primary_key": primary_key_candidate,
        "row_count": len(df)
    }
