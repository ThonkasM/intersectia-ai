import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings

BASE_DIR = Path(__file__).resolve().parents[2]


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path


@lru_cache(maxsize=1)
def load_topics() -> list[dict]:
    path = resolve_path(get_settings().topics_path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["topics"]
