import pytest
from fastapi.testclient import TestClient

import app.policy.infer as infer_module
from app.core.config import get_settings
from app.main import app
from app.policy.model import HeuristicPolicy

client = TestClient(app)
TOKEN = get_settings().internal_service_token


@pytest.fixture(autouse=True)
def use_heuristic_policy(monkeypatch):
    monkeypatch.setattr(infer_module, "_policy", HeuristicPolicy())


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


def test_decision_accepts_occupant():
    resp = client.post(
        "/decision",
        headers={"X-Internal-Token": TOKEN},
        json={
            "queue": [{"id": "a", "from": "N", "waitedSeconds": 2.0}],
            "occupant": {"id": "occ", "from": "E", "waitedSeconds": 0.0},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["vehicleId"] in {"a", None}


def test_decision_empty_queue_returns_null():
    resp = client.post(
        "/decision",
        headers={"X-Internal-Token": TOKEN},
        json={"queue": []},
    )
    assert resp.status_code == 200
    assert resp.json() == {"vehicleId": None}