from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pathlib import Path
import shutil
import uuid
import pandas as pd
from app.config import RAW_DATA_DIR
from app.ingestion.loader import load_file_to_duckdb
from app.ingestion.file_parser import parse_uploaded_file
from app.db.duckdb_client import db_client
from app.engine.profiler import profile_table, get_active_profile

router = APIRouter()

# Memory cache for ingestion background tasks
_ingestion_tasks = {}

def process_file_in_background(task_id: str, file_path: Path):
    """Executes file loading, text parsing, database indexing, and profiling in a background thread."""
    global _ingestion_tasks
    try:
        _ingestion_tasks[task_id] = {
            "status": "PROCESSING",
            "progress": 5,
            "message": "Initializing document ingestion..."
        }
        
        ext = file_path.suffix.lower()
        table_name = file_path.stem.lower().replace("-", "_").replace(" ", "_")

        if ext == ".pdf":
            # Smart PDF extractor: auto-detects scanned PDFs and uses OCR
            from app.ingestion.pdf_extractor import smart_extract_pdf
            
            def pdf_progress(idx, total, method):
                current_prog = 10 + int((idx / total) * 40)
                _ingestion_tasks[task_id] = {
                    "status": "PROCESSING",
                    "progress": current_prog,
                    "message": f"{method}: page {idx + 1}/{total}..."
                }
            
            _ingestion_tasks[task_id] = {
                "status": "PROCESSING",
                "progress": 10,
                "message": "Analyzing PDF structure..."
            }
            
            pages_data = smart_extract_pdf(str(file_path), progress_callback=pdf_progress)
            df = pd.DataFrame(pages_data)
        else:
            _ingestion_tasks[task_id] = {
                "status": "PROCESSING",
                "progress": 25,
                "message": "Parsing spreadsheet records..."
            }
            df, _ = parse_uploaded_file(file_path)

        # Standardize column headers
        df.columns = [str(col).strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns]

        if ext == ".pdf":
            table_name = "documents"
            _ingestion_tasks[task_id] = {
                "status": "PROCESSING",
                "progress": 60,
                "message": f"Appending {len(df)} records into DuckDB table '{table_name}'..."
            }
            db_client.append_df(table_name, df)
        else:
            _ingestion_tasks[task_id] = {
                "status": "PROCESSING",
                "progress": 60,
                "message": f"Writing {len(df)} records into DuckDB table '{table_name}'..."
            }
            db_client.load_df(table_name, df)

        _ingestion_tasks[task_id] = {
            "status": "PROCESSING",
            "progress": 80,
            "message": "Analyzing schema and generating dynamic AI profiles..."
        }
        
        profile_table(table_name)

        _ingestion_tasks[task_id] = {
            "status": "SUCCESS",
            "progress": 100,
            "message": f"Successfully loaded '{file_path.name}'!",
            "result": {
                "filename": file_path.name,
                "table_name": table_name,
                "rows_inserted": len(df),
                "columns_detected": list(df.columns)
            }
        }
    except Exception as e:
        print(f"Background Ingestion Failed for task {task_id}:", e)
        _ingestion_tasks[task_id] = {
            "status": "FAILED",
            "progress": 100,
            "message": f"File Ingestion Error: {str(e)}"
        }

@router.post("/ingest")
def upload_and_ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Uploads file and spawns a background thread task to prevent client request timeouts."""
    try:
        task_id = str(uuid.uuid4())
        dest_path = RAW_DATA_DIR / file.filename
        
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        _ingestion_tasks[task_id] = {
            "status": "PENDING",
            "progress": 0,
            "message": "Uploading file to server..."
        }

        # Spawn background process thread
        background_tasks.add_task(process_file_in_background, task_id, dest_path)
        
        return {"task_id": task_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File Upload Error: {str(e)}")

@router.get("/ingest/status/{task_id}")
def check_ingestion_status(task_id: str):
    """Returns ingestion progress percentage and current status for client polling."""
    if task_id not in _ingestion_tasks:
        raise HTTPException(status_code=404, detail="Ingestion task not found")
    return _ingestion_tasks[task_id]

@router.get("/table-profile")
def fetch_active_table_profile():
    """Returns the generated suggested queries and insights for the active dataset."""
    return get_active_profile()

@router.post("/demo-data")
def seed_demo_dataset():
    """Generates synthetic 1,000 Industrial Machine dataset in DuckDB."""
    try:
        result = generate_demo_dataset()
        profile_table("machines")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo Seed Error: {str(e)}")

@router.get("/documents")
def list_uploaded_documents():
    """Returns list of unique filenames in the documents table."""
    try:
        tables = db_client.list_tables()
        if 'documents' not in tables:
            return {"documents": []}
        rows = db_client.execute_query(
            "SELECT DISTINCT filename, COUNT(*) as pages FROM documents GROUP BY filename ORDER BY filename"
        )
        return {"documents": rows}
    except Exception as e:
        return {"documents": [], "error": str(e)}

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    """Deletes all pages of a specific document from the documents table."""
    try:
        tables = db_client.list_tables()
        if 'documents' not in tables:
            raise HTTPException(status_code=404, detail="No documents table found")
        db_client.execute_raw(f"DELETE FROM documents WHERE filename = '{filename}'")
        remaining = db_client.execute_query("SELECT COUNT(*) as cnt FROM documents")[0]["cnt"]
        if remaining == 0:
            db_client.conn.execute("DROP TABLE IF EXISTS documents CASCADE")
        return {"status": "deleted", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{filename}/rename")
def rename_document(filename: str, new_name: str):
    """Renames a document (updates filename column) in the documents table."""
    try:
        tables = db_client.list_tables()
        if 'documents' not in tables:
            raise HTTPException(status_code=404, detail="No documents table found")
        db_client.execute_raw(f"UPDATE documents SET filename = '{new_name}' WHERE filename = '{filename}'")
        return {"status": "renamed", "old_name": filename, "new_name": new_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
