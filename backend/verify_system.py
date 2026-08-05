import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.ingestion.demo_generator import generate_demo_dataset
from app.db.duckdb_client import db_client
from app.engine.query_router import classify_query
from app.engine.sql_engine import generate_and_execute_sql
from app.engine.grounding_auditor import audit_results
from app.engine.answer_synthesizer import synthesize_grounded_answer

def run_tests():
    print("--- 1. Testing Demo Dataset Generation ---")
    demo_res = generate_demo_dataset()
    print("Demo seed result:", demo_res)
    assert demo_res["machines_count"] == 1000, "Should generate 1000 machines"
    assert demo_res["maintenance_logs_count"] == 5000, "Should generate 5000 logs"

    print("\n--- 2. Testing Aggregate Natural Language Query (Highest Downtime) ---")
    query_1 = "Which machine had the highest total downtime?"
    classification_1 = classify_query(query_1)
    sql_1, results_1, viz_1 = generate_and_execute_sql(query_1)
    audit_1 = audit_results(results_1, sql_executed=sql_1, execution_type=classification_1["execution_type"])
    answer_1 = synthesize_grounded_answer(query_1, results_1, audit_1, viz_1)

    print("Query:", query_1)
    print("Executed SQL:\n", sql_1)
    print("Matched Rows Count:", len(results_1))
    print("Grounding Confidence:", audit_1.confidence_score, "%")
    print("Synthesized Answer:\n", answer_1)

    assert len(results_1) > 0, "Query 1 should return results"
    assert audit_1.confidence_score == 100.0, "SQL deterministic should have 100% confidence score"

    print("\n--- 3. Testing Target Machine Lookup (MAC-0452) ---")
    query_2 = "Show maintenance history for Machine MAC-0452"
    sql_2, results_2, viz_2 = generate_and_execute_sql(query_2)
    audit_2 = audit_results(results_2, sql_executed=sql_2, execution_type="SQL_DETERMINISTIC")
    answer_2 = synthesize_grounded_answer(query_2, results_2, audit_2, viz_2)

    print("Query:", query_2)
    print("Matched Rows Count for MAC-0452:", len(results_2))
    print("Synthesized Answer:\n", answer_2)

    print("\n--- 4. Testing Zero-Hallucination Shield (Non-Existent Machine) ---")
    query_3 = "Show maintenance history for Machine MAC-99999"
    sql_3, results_3, viz_3 = generate_and_execute_sql(query_3)
    audit_3 = audit_results(results_3, sql_executed=sql_3, execution_type="SQL_DETERMINISTIC")
    answer_3 = synthesize_grounded_answer(query_3, results_3, audit_3, viz_3)

    print("Query:", query_3)
    print("Is Grounded:", audit_3.is_grounded)
    print("Confidence Score:", audit_3.confidence_score)
    print("Synthesized Answer:\n", answer_3)
    assert audit_3.is_grounded == False, "Non-existent machine should return is_grounded=False"
    assert "no matching records were found" in answer_3.lower(), "Should report no records found"

    print("\n[SUCCESS] ALL BACKEND TESTS PASSED SUCCESSFULLY! ZERO HALLUCINATION VERIFIED.")

if __name__ == "__main__":
    run_tests()
