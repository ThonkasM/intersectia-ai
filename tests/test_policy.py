from app.models.schemas import QueuedVehicle
from app.policy.infer import encode_state, infer
from app.policy.model import HeuristicPolicy, QTable


def vehicle(vehicle_id, direction, waited):
    return QueuedVehicle(id=vehicle_id, **{"from": direction}, waitedSeconds=waited)


def test_empty_queue_returns_none():
    assert infer([]) is None


def test_single_vehicle_returns_its_id():
    assert infer([vehicle("a", "N", 1.0)]) == "a"


def test_highest_waited_seconds_wins():
    queue = [vehicle("low", "N", 1.0), vehicle("mid", "E", 5.0), vehicle("high", "S", 9.0)]
    assert infer(queue) == "high"


def test_tie_break_lowest_id_wins():
    queue = [vehicle("v2", "N", 3.0), vehicle("v1", "S", 3.0), vehicle("v0", "E", 3.0)]
    assert infer(queue) == "v0"


def test_heuristic_policy_returns_winning_index():
    policy = HeuristicPolicy()
    queue = [vehicle("a", "N", 2.0), vehicle("b", "E", 8.0)]
    assert policy.predict(queue) == 1


def test_heuristic_policy_empty_returns_none():
    assert HeuristicPolicy().predict([]) is None


def test_qtable_predict_returns_in_range_index():
    qtable = QTable()
    queue = [vehicle("a", "N", 2.0), vehicle("b", "E", 8.0)]
    index = qtable.predict(queue)
    assert 0 <= index < len(queue)


def test_encode_state_shape():
    queue = [vehicle("a", "N", 2.0), vehicle("b", "E", 8.0), vehicle("c", "E", 1.0)]
    state = encode_state(queue)
    assert state == (3, 8.0, 11.0, 1, 0, 2, 0)