import logging
import math
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from app.rag.embeddings import embed, tokenize
from app.rag.loader import BASE_DIR

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge_base"
MAX_CHUNK_CHARS = 700


@dataclass
class Chunk:
    source: str
    text: str
    vector: Counter = field(default_factory=Counter)


def _chunk_text(text: str, source: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    current: list[str] = []
    size = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current:
                body = " ".join(current)
                chunks.append(Chunk(source, body, embed(body)))
                current = []
                size = 0
            continue
        starts_section = line.startswith("#")
        if current and (starts_section or size >= MAX_CHUNK_CHARS):
            body = " ".join(current)
            chunks.append(Chunk(source, body, embed(body)))
            current = []
            size = 0
        current.append(line.lstrip("# ").strip())
        size += len(line)
    if current:
        body = " ".join(current)
        chunks.append(Chunk(source, body, embed(body)))
    return chunks


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.df: Counter = Counter()
        for chunk in chunks:
            self.df.update(set(chunk.vector))

    @classmethod
    def from_directory(cls, directory: Path) -> "Retriever":
        chunks: list[Chunk] = []
        if directory.exists():
            for path in sorted(directory.rglob("*")):
                if path.suffix.lower() not in (".md", ".txt"):
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    logger.warning("No se pudo leer %s", path, exc_info=True)
                    continue
                chunks.extend(_chunk_text(text, path.name))
        logger.info("Retriever cargó %d fragmentos desde %s", len(chunks), directory)
        return cls(chunks)

    def _idf(self, term: str) -> float:
        total = len(self.chunks) or 1
        return math.log((1 + total) / (1 + self.df.get(term, 0))) + 1.0

    def search(
        self, query: str, top_k: int = 3, min_score: float = 0.35
    ) -> list[Chunk]:
        if not self.chunks:
            return []
        terms = tokenize(query)
        if not terms:
            return []
        scored: list[tuple[float, Chunk]] = []
        for chunk in self.chunks:
            score = sum(
                self._idf(term) for term in set(terms) if term in chunk.vector
            ) / math.sqrt(len(terms))
            if score >= min_score:
                scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever.from_directory(KNOWLEDGE_DIR)
