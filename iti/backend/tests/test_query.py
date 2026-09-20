import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Test GET /health returns 200 status code and expected schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_store_loaded" in data
    assert "ollama_connected" in data

def test_query_happy_path():
    """Test POST /query with valid question returns 200 OK, answer, and sources list."""
    payload = {"question": "What are the admission requirements for ITI 9-Month program?", "top_k": 2}
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert isinstance(data["sources"], list)

def test_query_invalid_input_empty_payload():
    """Test POST /query with missing question yields 422 Unprocessable Entity."""
    payload = {}
    response = client.post("/query", json=payload)
    assert response.status_code == 422

def test_query_invalid_input_empty_string():
    """Test POST /query with empty string question yields 422 Unprocessable Entity."""
    payload = {"question": ""}
    response = client.post("/query", json=payload)
    assert response.status_code == 422
