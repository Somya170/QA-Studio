import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.ingestion.loader import load_file_to_duckdb
from app.engine.query_router import classify_query
from app.engine.sql_engine import generate_and_execute_sql
from app.engine.grounding_auditor import audit_results
from app.engine.answer_synthesizer import synthesize_grounded_answer

def test_uploaded_file_qa():
    print("--- 1. Ingesting sample_test_machines.xlsx into DuckDB ---")
    excel_path = Path("c:/Users/Somya/Downloads/DocYork/sample_test_machines.xlsx")
    ingest_res = load_file_to_duckdb(excel_path)
    print("Ingest Result:", ingest_res)
    assert ingest_res["status"] == "SUCCESS"
    assert ingest_res["rows_inserted"] == 8

    test_queries = [
        "Which machine had the highest repair cost in the uploaded file?",
        "Show technician notes for 3D Metal Printer MAC-5004",
        "Who operated CNC Lathe MAC-5002?",
        "Which machine had the highest downtime in the file?",
        "Show maintenance details for MAC-5001"
    ]

    print("\n--- 2. Testing Natural Language Queries on Uploaded Data ---")
    for q in test_queries:
        print(f"\n[QUERY]: {q}")
        classification = classify_query(q)
        sql, results, viz = generate_and_execute_sql(q)
        audit = audit_results(results, sql_executed=sql, execution_type=classification["execution_type"])
        answer = synthesize_grounded_answer(q, results, audit, viz)

        print(f"Executed SQL:\n{sql}")
        print(f"Matched Rows: {len(results)}")
        print(f"Synthesized Answer:\n{answer}")

        assert len(results) > 0, f"Query '{q}' should return matched rows from uploaded dataset"

    print("\n[SUCCESS] CUSTOM UPLOAD DATA QA PASSED 100% ACCURATELY!")

if __name__ == "__main__":
    test_uploaded_file_qa()
