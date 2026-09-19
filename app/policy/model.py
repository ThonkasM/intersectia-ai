import json
import logging
import pickle
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

DIRECTIONS = ("N", "S", "E", "W")


def _id(v):
    return v.id if hasattr(v, "id") else v["id"]


def _from(v):
    return v.from_ if hasattr(v, "from_") else v["from"]


def _waited(v):
    return v.waitedSeconds if hasattr(v, "waitedSeconds") else v["waited"]


def _occupant_axis(occupant):
    if occupant is None:
        return 0
    if isinstance(occupant, str):
        return 1 if occupant == "NS" else 2
    return 1 if _from(occupant) in ("N", "S") else 2


def encode_features(queue, occupant=None, wait_bin_size=5.0, max_bin=3):
    counts = {d: 0 for d in DIRECTIONS}
    waits = {d: 0.0 for d in DIRECTIONS}
    for vehicle in queue:
        counts[_from(vehicle)] += 1
        waits[_from(vehicle)] = max(waits[_from(vehicle)], _waited(vehicle))
    state = []
    for direction in DIRECTIONS:
        state.append(min(counts[direction], 3))
        state.append(min(int(waits[direction] / wait_bin_size), max_bin))
    state.append(_occupant_axis(occupant))
    return tuple(state)


class HeuristicPolicy:
    def predict(self, queue, occupant=None):
        del occupant
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

    def _encode(self, queue, occupant=None):
        return encode_features(
            queue, occupant, self.wait_bin_size, self.max_bin
        )

    def predict(self, queue, occupant=None):
        if not queue:
            return None
        state = self._encode(queue, occupant)
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

    def to_dict(self) -> dict:
        return {
            "wait_bin_size": self.wait_bin_size,
            "max_bin": self.max_bin,
            "q": [
                {"state": list(state), "pos": pos, "value": value}
                for (state, pos), value in self.q.items()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QTable":
        table = cls(
            wait_bin_size=float(data.get("wait_bin_size", 5.0)),
            max_bin=int(data.get("max_bin", 3)),
        )
        for entry in data.get("q", []):
            state = tuple(int(value) for value in entry["state"])
            table.q[(state, int(entry["pos"]))] = float(entry["value"])
        return table


def load_json_policy(path: Path) -> QTable:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return QTable.from_dict(data)


def load_trained_policy():
    path = Path(get_settings().trained_policy_path)
    if not path.exists():
        logger.info("No trained policy at %s; using HeuristicPolicy", path)
        return HeuristicPolicy()
    try:
        if path.suffix == ".json":
            policy = load_json_policy(path)
        else:
            with open(path, "rb") as handle:
                policy = pickle.load(handle)
    except Exception:
        logger.warning(
            "Failed to load trained policy at %s; using HeuristicPolicy",
            path,
            exc_info=True,
        )
        return HeuristicPolicy()
    if not hasattr(policy, "predict"):
        logger.warning(
            "Trained policy at %s has no predict(); using HeuristicPolicy", path
        )
        return HeuristicPolicy()
    logger.info("Loaded trained policy from %s (%s)", path, type(policy).__name__)
    return policy