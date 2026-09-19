import logging
from numbers import Integral

from app.policy.model import HeuristicPolicy, load_trained_policy

logger = logging.getLogger(__name__)

_policy = load_trained_policy()
_FALLBACK = HeuristicPolicy()


def encode_state(queue):
    from_counts = {d: 0 for d in ("N", "S", "E", "W")}
    for vehicle in queue:
        from_counts[vehicle.from_] += 1
    n_vehicles = len(queue)
    max_waited = max((vehicle.waitedSeconds for vehicle in queue), default=0.0)
    sum_waited = sum(vehicle.waitedSeconds for vehicle in queue)
    return (
        n_vehicles,
        max_waited,
        sum_waited,
        from_counts["N"],
        from_counts["S"],
        from_counts["E"],
        from_counts["W"],
    )


def _policy_decision(queue, occupant=None):
    decision = _policy.predict(queue, occupant)
    if isinstance(decision, bool):
        return None
    if isinstance(decision, Integral):
        index = int(decision)
        if 0 <= index < len(queue):
            return queue[index].id
        return None
    if isinstance(decision, str):
        for vehicle in queue:
            if vehicle.id == decision:
                return vehicle.id
    return None


def infer(queue, occupant=None):
    if not queue:
        return None
    try:
        vehicle_id = _policy_decision(queue, occupant)
    except Exception:
        logger.warning("policy prediction failed; using heuristic fallback", exc_info=True)
        vehicle_id = None
    if vehicle_id is not None:
        return vehicle_id
    decision = _FALLBACK.predict(queue, occupant)
    if decision is None:
        return None
    return queue[decision].id
