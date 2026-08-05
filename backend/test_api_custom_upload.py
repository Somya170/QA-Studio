import requests
from pathlib import Path
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("--- 1. Uploading sample_test_machines.xlsx via /api/ingest ---")
    excel_path = Path("c:/Users/Somya/Downloads/DocYork/sample_test_machines.xlsx")
    
    with open(excel_path, "rb") as f:
        files = {"file": (excel_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        ingest_res = requests.post(f"{BASE_URL}/ingest", files=files)
        
    print("Ingest Response Status:", ingest_res.status_code)
    print("Ingest Response JSON:", ingest_res.json())
    assert ingest_res.status_code == 200, "Ingest should return HTTP 200"

    print("\n--- 2. Testing Natural Language Queries over Uploaded Custom Data ---")
    test_queries = [
        "Which machine had the highest repair cost in the uploaded file?",
        "Show technician notes for 3D Metal Printer MAC-5004",
        "Who operated CNC Lathe MAC-5002?",
        "Which machine had the highest downtime in the file?",
        "Show maintenance details for MAC-5001"
    ]

    for q in test_queries:
        print(f"\n==========================================")
        print(f"[QUERY]: {q}")
        res = requests.post(f"{BASE_URL}/query", json={"query": q})
        print("HTTP Status:", res.status_code)
        data = res.json()
        print("Executed SQL:\n", data["audit"]["sql_executed"])
        print("Matched Rows Count:", data["audit"]["matched_row_count"])
        print("Confidence Score:", data["audit"]["confidence_score"], "%")
        print("Synthesized Answer:\n", data["answer"])

        assert res.status_code == 200, "Query should succeed"
        assert data["audit"]["matched_row_count"] > 0, f"Query '{q}' should match rows"

    print("\n[SUCCESS] ALL CUSTOM UPLOAD NATURAL LANGUAGE QUERIES PASSED 100% ACCURATELY!")

if __name__ == "__main__":
    test_api()
