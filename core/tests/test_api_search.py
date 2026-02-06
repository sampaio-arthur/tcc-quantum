from fastapi.testclient import TestClient

from infrastructure.api.fastapi_app import app


client = TestClient(app)


def test_search_endpoint():
    payload = {
        "query": "algoritmos",
        "documents": ["algoritmos", "outra coisa"],
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "algoritmos"
    assert len(data["results"]) == 2
    assert data["answer"]


def test_search_file_endpoint_txt():
    response = client.post(
        "/search/file",
        data={"query": "algoritmos"},
        files={"file": ("doc.txt", b"algoritmos", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "algoritmos"
    assert len(data["results"]) == 1
    assert data["answer"]
