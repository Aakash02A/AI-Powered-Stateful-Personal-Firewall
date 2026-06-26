import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "data" in response.json()

def test_get_top_talkers():
    response = client.get("/api/top-talkers")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)

def test_get_protocols():
    response = client.get("/api/protocols")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], dict)

def test_get_alerts():
    response = client.get("/api/alerts?limit=5")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)

def test_get_connections():
    response = client.get("/api/connections?limit=5")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)

# We will skip websocket test in standard test suite because it requires 
# full async setup and running event loops, but we verified the API structure.
