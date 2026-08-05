import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"

def test_shift_queries():
    print("--- 1. Re-ingesting sample_test_machines.xlsx ---")
    excel_path = Path("c:/Users/Somya/Downloads/DocYork/sample_test_machines.xlsx")
    with open(excel_path, "rb") as f:
        requests.post(f"{BASE_URL}/ingest", files={"file": (excel_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})

    queries = [
        "what is sunita Verma shift timing",
        "what is sunita Verma shift timing and technician notes?"
    ]

    for q in queries:
        print(f"\n==========================================")
        print(f"[QUERY]: {q}")
        res = requests.post(f"{BASE_URL}/query", json={"query": q})
        print("Status Code:", res.status_code)
        data = res.json()
        print("Executed SQL:\n", data["audit"]["sql_executed"])
        print("Matched Row Count:", data["audit"]["matched_row_count"])
        print("Synthesized Answer:\n", data["answer"])

        assert res.status_code == 200
        assert "Sunita Verma" in data["answer"]
        assert "Night (22:00-06:00)" in data["answer"]

    print("\n[SUCCESS] BOTH SUNITA VERMA SHIFT TIMING QUERIES PASSED PERFECTLY!")

if __name__ == "__main__":
    test_shift_queries()
