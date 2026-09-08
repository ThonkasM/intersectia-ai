import pickle
import random
from pathlib import Path

from app.core.config import get_settings
from app.policy.model import DIRECTIONS, QTable

EPISODES = 400
HORIZON = 8
ALPHA = 0.1
GAMMA = 0.9
EPSILON_START = 0.2
EPSILON_MIN = 0.05
ARRIVAL_PROB = 0.5
MAX_VEHICLES = 8


class IntersectionEnv:
    def __init__(self, rng):
        self.rng = rng
        self.reset()

    def reset(self):
        self.vehicles = []
        self.t = 0
        return self._state()

    def _state(self):
        counts = {d: 0 for d in DIRECTIONS}
        waits = {d: 0.0 for d in DIRECTIONS}
        for vehicle in self.vehicles:
            counts[vehicle["from"]] += 1
            waits[vehicle["from"]] = max(waits[vehicle["from"]], vehicle["waited"])
        state = []
        for direction in DIRECTIONS:
            state.append(min(counts[direction], 3))
            state.append(min(int(waits[direction] / 5.0), 3))
        return tuple(state)

    def _sorted(self):
        return sorted(self.vehicles, key=lambda v: (-v["waited"], v["id"]))

    def step(self, action):
        reward = -sum(vehicle["waited"] for vehicle in self.vehicles)
        ordered = self._sorted()
        if action is not None and ordered:
            self.vehicles.remove(ordered[action])
        for vehicle in self.vehicles:
            vehicle["waited"] += 1.0
        if len(self.vehicles) < MAX_VEHICLES:
            for direction in DIRECTIONS:
                if self.rng.random() < ARRIVAL_PROB:
                    vehicle_id = f"{direction}{self.rng.randint(100, 999)}"
                    self.vehicles.append({"id": vehicle_id, "from": direction, "waited": 0.0})
        self.t += 1
        return self._state(), reward, self.t >= HORIZON


def train() -> QTable:
    rng = random.Random(0)
    env = IntersectionEnv(rng)
    qtable = QTable()
    for episode in range(EPISODES):
        epsilon = max(EPSILON_MIN, EPSILON_START * (1.0 - episode / EPISODES))
        state = env.reset()
        while True:
            ordered = env._sorted()
            if ordered:
                if rng.random() < epsilon:
                    action = rng.randrange(len(ordered))
                else:
                    action = qtable.predict(ordered)
                    if action is None:
                        action = rng.randrange(len(ordered))
            else:
                action = None
            next_state, reward, done = env.step(action)
            if action is not None:
                key = (state, action)
                current = qtable.q.get(key, 0.0)
                best_next = 0.0
                if env.vehicles:
                    best_next = max(qtable.q.get((next_state, k), 0.0) for k in range(len(env.vehicles)))
                qtable.q[key] = current + ALPHA * (reward + GAMMA * best_next - current)
            state = next_state
            if done:
                break
    return qtable


if __name__ == "__main__":
    policy = train()
    path = Path(get_settings().trained_policy_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        pickle.dump(policy, handle)
    print(f"saved trained policy to {path} ({len(policy.q)} Q entries)")