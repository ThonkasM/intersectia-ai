import json

from app.policy.model import HeuristicPolicy, QTable, load_json_policy
from app.policy.train import evaluate, train


def test_train_produces_qtable_entries():
    policy = train(episodes=120, seed=0)
    assert isinstance(policy, QTable)
    assert len(policy.q) > 0


def test_to_dict_roundtrip_preserves_predictions():
    policy = train(episodes=120, seed=0)
    clone = QTable.from_dict(policy.to_dict())
    queue = [
        {"id": "a", "from": "N", "waited": 2.0},
        {"id": "b", "from": "E", "waited": 8.0},
    ]
    assert clone.predict(queue) == policy.predict(queue)


def test_load_json_policy(tmp_path):
    policy = train(episodes=60, seed=0)
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy.to_dict()), encoding="utf-8")
    loaded = load_json_policy(path)
    assert len(loaded.q) == len(policy.q)


def test_evaluate_returns_metrics():
    metrics = evaluate(HeuristicPolicy(), episodes=20, seed=1)
    assert set(metrics) == {"total_cost", "crossings", "avg_cost"}
    assert metrics["crossings"] > 0
