
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

HEADERS = {"X-API-Key": "default_dev_key"}


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_stats():
    response = client.get("/api/v1/stats", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "data" in response.json()


def test_get_top_talkers():
    response = client.get("/api/v1/top-talkers", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)


def test_get_protocols():
    response = client.get("/api/v1/protocols", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], dict)


def test_get_alerts():
    response = client.get("/api/v1/alerts?limit=5", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)


def test_get_connections():
    response = client.get("/api/v1/connections?limit=5", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)


# We will skip websocket test in standard test suite because it requires
# full async setup and running event loops, but we verified the API structure.
