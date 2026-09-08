import json
from functools import lru_cache

from app.core.config import get_settings


@lru_cache(maxsize=1)
def load_topics() -> list[dict]:
    path = get_settings().topics_path
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["topics"]