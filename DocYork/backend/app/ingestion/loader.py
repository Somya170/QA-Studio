from pathlib import Path
from app.db.duckdb_client import db_client
from app.ingestion.file_parser import parse_uploaded_file
from app.ingestion.schema_detector import detect_schema_and_relationships

def load_file_to_duckdb(file_path: Path):
    """Parses and loads file into DuckDB, returning summary metadata."""
    df, table_name = parse_uploaded_file(file_path)
    metadata = detect_schema_and_relationships(df, table_name)
    
    db_client.load_df(table_name, df)
    
    return {
        "filename": file_path.name,
        "table_name": table_name,
        "rows_inserted": len(df),
        "columns_detected": list(df.columns),
        "status": "SUCCESS"
    }
