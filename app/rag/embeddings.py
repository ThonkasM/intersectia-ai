import math
import re
import unicodedata
from collections import Counter

_WORD = re.compile(r"[a-z0-9]+")
_MARKS = re.compile(r"[\u0300-\u036f]")

# Palabras vacias (es/en) que no aportan a la recuperacion y generan falsos matches
# (p. ej. "cuanto es 2 + 2" NO debe matchear documentos por "es"/"2").
STOPWORDS = {
    # espanol
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "u",
    "que", "en", "con", "por", "para", "del", "al", "se", "su", "sus", "es",
    "son", "era", "fue", "como", "cuanto", "cuanta", "cuantos", "cuantas",
    "cual", "cuales", "quien", "quienes", "donde", "cuando", "porque", "mas",
    "pero", "si", "no", "mi", "tu", "te", "me", "nos", "lo", "le", "les",
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aqui",
    "hay", "muy", "ya", "sin", "sobre", "entre", "hasta", "desde", "tambien",
    "ser", "hola", "buenas", "gracias", "dime", "explica", "explicame",
    "sabes", "tiene", "tengo", "puede", "puedo", "hacer", "hace",
    # english
    "the", "and", "are", "was", "were", "be", "been", "what", "how", "why",
    "where", "when", "who", "which", "does", "did", "can", "could", "would",
    "should", "you", "it", "we", "they", "she", "this", "that", "these",
    "those", "there", "here", "your", "tell", "about",
}


def tokenize(text: str) -> list[str]:
    normalized = _MARKS.sub("", unicodedata.normalize("NFD", text.lower()))
    return _WORD.findall(normalized)


def meaningful_terms(terms: list[str]) -> list[str]:
    """Descarta stopwords, tokens de 1-2 letras y numeros sueltos."""
    return [t for t in terms if len(t) >= 3 and t not in STOPWORDS and not t.isdigit()]


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
