from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)
TOKEN = get_settings().internal_service_token


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_decision_without_token_forbidden():
    resp = client.post("/decision", json={"queue": []})
    assert resp.status_code == 403


def test_decision_returns_longest_waiting_vehicle():
    resp = client.post(
        "/decision",
        headers={"X-Internal-Token": TOKEN},
        json={
            "queue": [
                {"id": "a", "from": "N", "waitedSeconds": 2.0},
                {"id": "b", "from": "E", "waitedSeconds": 7.0},
                {"id": "c", "from": "S", "waitedSeconds": 4.0},
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"vehicleId": "b"}


def test_decision_with_occupant_returns_null():
    resp = client.post(
        "/decision",
        headers={"X-Internal-Token": TOKEN},
        json={
            "queue": [{"id": "a", "from": "N", "waitedSeconds": 2.0}],
            "occupant": {"id": "occ", "from": "E", "waitedSeconds": 0.0},
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"vehicleId": None}