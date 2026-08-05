import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_location_query():
    q = "What is the location of MAC-5007?"
    print(f"[QUERY]: {q}")
    res = requests.post(f"{BASE_URL}/query", json={"query": q})
    print("Status Code:", res.status_code)
    data = res.json()
    print("Answer:\n", data["answer"])
    
    assert res.status_code == 200
    assert "Logistics Warehouse" in data["answer"]
    assert "MAC-5007" in data["answer"]
    print("\n[SUCCESS] LOCATION QUERY TEST PASSED PERFECTLY!")

if __name__ == "__main__":
    test_location_query()
