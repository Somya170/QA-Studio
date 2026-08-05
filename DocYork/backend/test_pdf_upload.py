import requests
import os
import urllib.request

BASE_URL = "http://127.0.0.1:8000/api"

def download_sample_pdf(filename):
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    print(f"Downloading valid sample PDF from W3C: {url}")
    urllib.request.urlretrieve(url, filename)

def test_pdf_flow():
    pdf_filename = "sample_w3c_dummy.pdf"
    download_sample_pdf(pdf_filename)
    
    print("\n--- 1. Uploading PDF to /api/ingest ---")
    files = {"file": open(pdf_filename, "rb")}
    ingest_res = requests.post(f"{BASE_URL}/ingest", files=files)
    print("Ingest Status:", ingest_res.status_code)
    print("Ingest JSON:", ingest_res.json())
    
    print("\n--- 2. Fetching Table Profile ---")
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

    # Querying a word from the dummy PDF
    test_q = "What is inside the dummy PDF file?"
    print(f"\n--- 3. Testing Semantic QA: '{test_q}' ---")
    query_res = requests.post(f"{BASE_URL}/query", json={"query": test_q})
    print("Query Status:", query_res.status_code)
    query_data = query_res.json()
    print("Execution Type:", query_data["execution_type"])
    print("Answer:", query_data["answer"])

    # Clean up file
    try:
        os.remove(pdf_filename)
    except Exception:
        pass

if __name__ == "__main__":
    test_pdf_flow()
