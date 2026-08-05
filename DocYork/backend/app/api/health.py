from fastapi import APIRouter
from app.config import LLM_PROVIDER
from app.db.duckdb_client import db_client

router = APIRouter()

@router.get("/health")
def health_check():
    tables = db_client.list_tables()
    return {
        "status": "ONLINE",
        "service": "DocYork Precision Data QA Engine",
        "llm_provider": LLM_PROVIDER,
        "database_tables": tables,
        "mode": "Zero-Hallucination Production"
    }
