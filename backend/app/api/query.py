from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.engine.query_router import classify_query
from app.engine.sql_engine import generate_and_execute_sql
from app.engine.semantic_engine import perform_semantic_search
from app.engine.grounding_auditor import audit_results
from app.engine.answer_synthesizer import synthesize_grounded_answer
from app.engine.profiler import get_active_profile
from app.db.duckdb_client import db_client

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def execute_natural_language_query(request: QueryRequest):
    """Primary endpoint for Zero-Hallucination Natural Language Data QA."""
    try:
        # Step 1: Classify intent
        classification = classify_query(request.query)
        exec_type = classification["execution_type"]

        results = []
        sql_used = None
        viz_hint = "TABLE"

        # Check if active table is an unstructured PDF
        profile = get_active_profile()
        active_table = profile.get("table_name")
        is_pdf = False
        
        if active_table:
            try:
                cols = db_client.get_table_schema(active_table)
                is_pdf = len(cols) == 3 and any(c["column"].lower() == "text_content" for c in cols)
            except Exception:
                pass

        # Step 2: Query execution routing
        if is_pdf:
            # Skip SQL translation for prose PDFs and execute semantic match
            results = perform_semantic_search(request.query, filter_document=request.filter_document)
            exec_type = "SEMANTIC_TEXT"
        else:
            # Try SQL generation first for structured tables
            try:
                sql_used, results, viz_hint = generate_and_execute_sql(
                    request.query, request.filter_machine_id, request.filter_category
                )
            except Exception as e:
                print("SQL Generation failed:", e)

            # Fall back to semantic keyword search if SQL execution yielded no records
            if not results:
                results = perform_semantic_search(request.query, filter_document=request.filter_document)
                exec_type = "SEMANTIC_TEXT"
            else:
                if exec_type == "SEMANTIC_TEXT":
                    exec_type = "HYBRID"

        # Step 3: Audit grounding & verify proof
        audit = audit_results(results, sql_executed=sql_used, execution_type=exec_type)

        # Step 4: Synthesize grounded text answer
        answer = synthesize_grounded_answer(request.query, results, audit, viz_hint)

        return QueryResponse(
            query=request.query,
            answer=answer,
            execution_type=exec_type,
            audit=audit,
            data_table=results[:20],
            visualization_hint=viz_hint
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {str(e)}")
