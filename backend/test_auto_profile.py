import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_profiling():
    print("--- 1. Uploading sample_sales_inventory.xlsx ---")
    files = {"file": open("sample_sales_inventory.xlsx", "rb")}
    ingest_res = requests.post(f"{BASE_URL}/ingest", files=files)
    print("Ingest Status:", ingest_res.status_code)
    print("Ingest JSON:", ingest_res.json())
    
    print("\n--- 2. Fetching Auto-Generated Table Profile ---")
    profile_res = requests.get(f"{BASE_URL}/table-profile")
    print("Profile Status:", profile_res.status_code)
    profile_data = profile_res.json()
    print("Profile Table Name:", profile_data["table_name"])
    print("Suggested Queries:")
    for q in profile_data["suggested_queries"]:
        print(f"  - {q}")
    print("Summary Insights:")
    for ins in profile_data["summary_insights"]:
        print(f"  - {ins}")

    # Let's test asking one of the suggested queries to see if LLM translates it to SQL on the new table!
    if profile_data["suggested_queries"]:
        test_q = profile_data["suggested_queries"][0]
        print(f"\n--- 3. Testing Dynamic Query: '{test_q}' ---")
        query_res = requests.post(f"{BASE_URL}/query", json={"query": test_q})
        print("Query Status:", query_res.status_code)
        query_data = query_res.json()
        print("Executed SQL:", query_data["audit"]["sql_executed"])
        print("Answer:", query_data["answer"])

if __name__ == "__main__":
    test_profiling()
