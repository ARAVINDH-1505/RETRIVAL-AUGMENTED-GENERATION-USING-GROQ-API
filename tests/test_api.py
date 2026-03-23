import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the RAG API"}

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# We mock actual RAG query to avoid hitting the Groq API in basic CI checks
# unless GROQ_API_KEY is supplied to the test environment
def test_query_endpoint_missing_input():
    response = client.post("/api/query", json={})
    # Since input1 is required, it should throw a 422 Unprocessable Entity
    assert response.status_code == 422
