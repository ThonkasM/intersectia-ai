import json
import random
from pathlib import Path

from app.core.config import get_settings
from app.policy.model import (
    DIRECTIONS,
    HeuristicPolicy,
    QTable,
    encode_features,
)

EPISODES = 3000
HORIZON = 12
ALPHA = 0.15
GAMMA = 0.9
EPSILON_START = 0.3
EPSILON_MIN = 0.05
ARRIVAL_PROB = 0.5
MAX_VEHICLES = 8
SERVICE_TIME = 3
CONFLICT_PENALTY = 20.0


def _axis(vehicle) -> str:
    return "NS" if vehicle["from"] in ("N", "S") else "EW"


class IntersectionEnv:
    """Entorno simplificado de una intersección con eje ocupado.

    Se concede el paso a un vehículo; mientras un eje está ocupado (SERVICE_TIME
    pasos), solo se puede conceder a vehículos del mismo eje (los opuestos son
    compatibles). Conceder a un eje en conflicto no libera al vehículo y recibe
    una penalización: por eso importa el orden, no solo "el que más esperó".
    """

    def __init__(self, rng):
        self.rng = rng
        self.reset()

    def reset(self):
        self.vehicles = []
        self.t = 0
        self.occupant = None
        self.service_timer = 0
        return self._state()

    def _state(self):
        return encode_features(self.vehicles, self.occupant)

    def _sorted(self):
        return sorted(self.vehicles, key=lambda v: (-v["waited"], v["id"]))

    def step(self, action):
        reward = 0.0
        ordered = self._sorted()
        if action is not None and 0 <= action < len(ordered):
            chosen = ordered[action]
            axis = _axis(chosen)
            if self.occupant is None or self.occupant == axis:
                self.vehicles.remove(chosen)
                self.occupant = axis
                self.service_timer = SERVICE_TIME
                reward = chosen["waited"]
            else:
                reward = -CONFLICT_PENALTY
        if self.occupant is not None:
            self.service_timer -= 1
            if self.service_timer <= 0:
                self.occupant = None
        for vehicle in self.vehicles:
            vehicle["waited"] += 1.0
        if len(self.vehicles) < MAX_VEHICLES:
            for direction in DIRECTIONS:
                if self.rng.random() < ARRIVAL_PROB:
                    vehicle_id = f"{direction}{self.rng.randint(100, 999)}"
                    self.vehicles.append(
                        {"id": vehicle_id, "from": direction, "waited": 0.0}
                    )
        self.t += 1
        return self._state(), reward, self.t >= HORIZON


def _select_action(qtable, ordered, occupant, epsilon, rng):
    if not ordered:
        return None
    if rng.random() < epsilon:
        return rng.randrange(len(ordered))
    action = qtable.predict(ordered, occupant)
    return action if action is not None else rng.randrange(len(ordered))


def train(episodes: int = EPISODES, seed: int = 0) -> QTable:
    rng = random.Random(seed)
    env = IntersectionEnv(rng)
    qtable = QTable()
    for episode in range(episodes):
        epsilon = max(EPSILON_MIN, EPSILON_START * (1.0 - episode / episodes))
        state = env.reset()
        while True:
            ordered = env._sorted()
            action = _select_action(qtable, ordered, env.occupant, epsilon, rng)
            next_state, reward, done = env.step(action)
            if action is not None:
                key = (state, action)
                current = qtable.q.get(key, 0.0)
                best_next = 0.0
                if env.vehicles:
                    count = len(env._sorted())
                    best_next = max(
                        qtable.q.get((next_state, k), 0.0) for k in range(count)
                    )
                qtable.q[key] = current + ALPHA * (
                    reward + GAMMA * best_next - current
                )
            state = next_state
            if done:
                break
    return qtable


def _choose(policy, ordered, occupant, rng):
    if not ordered:
        return None
    if policy == "random":
        return rng.randrange(len(ordered))
    return policy.predict(ordered, occupant)


def evaluate(policy, episodes: int = 200, seed: int = 12345) -> dict:
    rng = random.Random(seed)
    env = IntersectionEnv(rng)
    total_wait = 0.0
    crossings = 0
    for _ in range(episodes):
        env.reset()
        while True:
            ordered = env._sorted()
            action = _choose(policy, ordered, env.occupant, rng)
            _, reward, done = env.step(action)
            total_wait += -reward
            if action is not None:
                crossings += 1
            if done:
                break
    return {
        "total_cost": round(total_wait, 2),
        "crossings": crossings,
        "avg_cost": round(total_wait / crossings, 3) if crossings else None,
    }


def main() -> None:
    trained = train()
    comparison = {
        "trained": evaluate(trained),
        "heuristic": evaluate(HeuristicPolicy()),
        "random": evaluate("random"),
    }
    path = Path(get_settings().trained_policy_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(trained.to_dict(), handle)
    print(f"saved trained policy to {path} ({len(trained.q)} Q entries)")
    print(json.dumps(comparison, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
