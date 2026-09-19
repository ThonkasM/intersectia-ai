import math
import re
import unicodedata
from collections import Counter

_WORD = re.compile(r"[a-z0-9]+")
_MARKS = re.compile(r"[\u0300-\u036f]")


def tokenize(text: str) -> list[str]:
    normalized = _MARKS.sub("", unicodedata.normalize("NFD", text.lower()))
    return _WORD.findall(normalized)


def embed(text: str) -> Counter:
    """Vector léxico (bolsa de palabras). Sin dependencias externas ni red."""
    return Counter(tokenize(text))


def cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    numerator = sum(a[token] * b[token] for token in common)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return numerator / (norm_a * norm_b)
