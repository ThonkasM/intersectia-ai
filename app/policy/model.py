import pickle
from pathlib import Path

from app.core.config import get_settings

DIRECTIONS = ("N", "S", "E", "W")


def _id(v):
    return v.id if hasattr(v, "id") else v["id"]


def _from(v):
    return v.from_ if hasattr(v, "from_") else v["from"]


def _waited(v):
    return v.waitedSeconds if hasattr(v, "waitedSeconds") else v["waited"]


class HeuristicPolicy:
    def predict(self, queue):
        best = None
        for i, vehicle in enumerate(queue):
            if best is None:
                best = i
                continue
            current = queue[best]
            if _waited(vehicle) > _waited(current) or (
                _waited(vehicle) == _waited(current) and _id(vehicle) < _id(current)
            ):
                best = i
        return best


class QTable:
    def __init__(self, q=None, wait_bin_size=5.0, max_bin=3):
        self.q = q if q is not None else {}
        self.wait_bin_size = wait_bin_size
        self.max_bin = max_bin

    def _encode(self, queue):
        counts = {d: 0 for d in DIRECTIONS}
        waits = {d: 0.0 for d in DIRECTIONS}
        for vehicle in queue:
            counts[_from(vehicle)] += 1
            waits[_from(vehicle)] = max(waits[_from(vehicle)], _waited(vehicle))
        state = []
        for direction in DIRECTIONS:
            state.append(min(counts[direction], 3))
            state.append(min(int(waits[direction] / self.wait_bin_size), self.max_bin))
        return tuple(state)

    def predict(self, queue):
        if not queue:
            return None
        state = self._encode(queue)
        ordered = sorted(
            range(len(queue)),
            key=lambda i: (-_waited(queue[i]), _id(queue[i])),
        )
        best_pos, best_q = 0, float("-inf")
        for pos in range(len(ordered)):
            value = self.q.get((state, pos), 0.0)
            if value > best_q:
                best_q, best_pos = value, pos
        return ordered[best_pos]


def load_trained_policy():
    path = Path(get_settings().trained_policy_path)
    if not path.exists():
        return HeuristicPolicy()
    try:
        with open(path, "rb") as handle:
            return pickle.load(handle)
    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError):
        return HeuristicPolicy()