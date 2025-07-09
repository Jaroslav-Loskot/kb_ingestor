import requests

BASE_URL = "http://127.0.0.1:8888"

def test_search_similar():
    sentence = "Foxy Fox is Foxy as Fox"

    # Step 1: Get embedding
    embed_response = requests.post(f"{BASE_URL}/embed", json={"text": sentence})
    assert embed_response.status_code == 200, f"Embedding failed: {embed_response.text}"
    embedding = embed_response.json()["embedding"]
    assert embedding and isinstance(embedding, list)

    # Step 2: Perform search
    search_response = requests.post(f"{BASE_URL}/search", json={
        "embedding": embedding,
        "top_k": 3,
        "table_name": "api_chunks",  # ✅ specify correct table
        "metadata" : {
            # "document_id": "seq-001"  # Optional: filter on metadata
        }
    })

    assert search_response.status_code == 200, f"Search failed: {search_response.text}"
    results = search_response.json()["matches"]

    # Step 3: Check results
    print("🔍 Top matches:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")

    assert isinstance(results, list)
    assert len(results) > 0
