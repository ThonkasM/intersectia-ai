import json
import logging
import re
import time
import unicodedata

from app.core.config import get_settings
from app.rag.loader import load_topics
from app.rag.retriever import Chunk, get_retriever
from app.services.bedrock_client import BedrockClient, BedrockUnavailableError

logger = logging.getLogger(__name__)

COMBINING_MARKS = re.compile(r"[\u0300-\u036f]")

GREETING_PATTERNS = [
    r"\b(hola|holi|holis|hey|saludos|salutaciones)\b",
    r"\bbuen(os)?\s*(dia|dias|tardes|noches|noche)\b",
    r"\bbuenas\b",
    r"\b(quien|que)\s*(eres|haces|sos)\b",
    r"\b(gracias|thank\s*(you|s)?|thx)\b",
    r"\b(ayuda|help|ayudame|ayudame|auxilio)\b",
]

FEELING_PATTERNS = [
    r"\bcomo\s*(estas|estas|estais|esta|te\s*va|te\s*sientes|andas|andamos|vamos|vas)\b",
    r"\bque\s*tal\b",
    r"\bcomo\s*estamos\b",
    r"\b(todo|va)\s*bien\b",
    r"\bque\s*(onda|hubo|cuentas|dices|cuenta|dice)\b",
]

GREETING_RESPONSE = (
    "¡Hola! Soy el Asistente de IntersectIA, tu guía sobre IoT, vehículos autónomos "
    "y el proyecto IntersectIA. Puedes preguntarme sobre IoT, vehículos autónomos y sus "
    "niveles, la relación V2V/V2I, la demo 3D, el modo tradicional vs el gestionado, "
    "y la IA de decisión. ¿En qué puedo ayudarte hoy?"
)

FEELING_RESPONSE = (
    "¡Aquí estoy, siempre listo para ayudarte! Soy el Asistente de IntersectIA y estoy aquí "
    "para resolver tus dudas sobre IoT, vehículos autónomos y la gestión autónoma de "
    "intersecciones. ¿Sobre qué tema te gustaría consultar hoy?"
)

NO_TOPIC_RESPONSE = (
    "Lo siento, no tengo información sobre ese tema. Intenta reformular tu pregunta o "
    "pregunta sobre IoT, vehículos autónomos, la demo 3D o la IA de decisión."
)


def _strip_accents(text: str) -> str:
    return COMBINING_MARKS.sub("", unicodedata.normalize("NFD", text))


def normalize(text: str) -> str:
    return re.sub(
        r"\s+", " ", re.sub(r"[^\w\s]", " ", _strip_accents(text.lower().strip()))
    ).strip()


def slugify(titulo: str) -> str:
    value = re.sub(r"[^\w\s-]", "", _strip_accents(titulo.lower()))
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


class ChatService:
    CONTEXT_TTL_MS = 5 * 60 * 1000
    MAX_SESSIONS = 500

    def __init__(self):
        settings = get_settings()
        self.topics = load_topics()
        self.bedrock = BedrockClient(settings.bedrock_model_id, settings.aws_region)
        self.retriever = get_retriever()
        self.conversation_context: dict[str, dict] = {}
        self._exact: dict[str, tuple[dict, str]] = {}
        self._keyword_topics: list[tuple[dict, list[str]]] = []
        for topic in self.topics:
            for pair in topic.get("preguntasRespuestas") or []:
                pregunta = pair.get("pregunta")
                respuesta = pair.get("respuesta")
                if pregunta and respuesta:
                    self._exact[normalize(pregunta)] = (topic, respuesta)
            keywords = [normalize(k) for k in (topic.get("keywords") or [])]
            self._keyword_topics.append((topic, [k for k in keywords if k]))

    def _remember(self, session_id: str, topic: dict) -> None:
        now = time.time() * 1000
        self.conversation_context[session_id] = {
            "slug": topic["slug"],
            "contextoGuia": topic.get("contextoGuia", ""),
            "timestamp": now,
        }
        if len(self.conversation_context) > self.MAX_SESSIONS:
            for sid, ctx in list(self.conversation_context.items()):
                if now - ctx["timestamp"] > self.CONTEXT_TTL_MS:
                    self.conversation_context.pop(sid, None)
            while len(self.conversation_context) > self.MAX_SESSIONS:
                oldest = min(
                    self.conversation_context,
                    key=lambda sid: self.conversation_context[sid]["timestamp"],
                )
                self.conversation_context.pop(oldest, None)

    def ask(self, message: str, session_id: str = "anon") -> str:
        normalized_question = normalize(message)

        exact = self._exact.get(normalized_question)
        if exact is not None:
            topic, respuesta = exact
            self._remember(session_id, topic)
            return respuesta

        for pattern in GREETING_PATTERNS:
            if re.search(pattern, normalized_question):
                self.conversation_context.pop(session_id, None)
                return GREETING_RESPONSE

        for pattern in FEELING_PATTERNS:
            if re.search(pattern, normalized_question):
                self.conversation_context.pop(session_id, None)
                return FEELING_RESPONSE

        best_topic = None
        best_count = 0
        for topic, keywords in self._keyword_topics:
            count = 0
            for normalized_keyword in keywords:
                escaped = re.escape(normalized_keyword)
                if re.search(rf"\b{escaped}\b", normalized_question):
                    count += 1
            if count > best_count:
                best_count = count
                best_topic = topic

        if best_topic and best_count >= 1:
            return self._answer_with_context(session_id, best_topic, message)

        previous_ctx = self.conversation_context.get(session_id)
        if previous_ctx and time.time() * 1000 - previous_ctx["timestamp"] < self.CONTEXT_TTL_MS:
            follow_up_prompt = (
                f'Eres un asistente de IntersectIA, un proyecto educativo sobre IoT y '
                f'vehículos autónomos. El usuario acaba de preguntar sobre '
                f'"{previous_ctx["slug"]}" y ahora hace una pregunta de seguimiento. '
                f"Responde ÚNICAMENTE basándote en el contexto proporcionado.\n"
                f"Tu respuesta debe ser en español, clara y concisa.\n"
                f'Devuelve tu respuesta en formato JSON exactamente así: '
                f'{{"respuesta": "texto de la respuesta"}}\n\n'
                f"Contexto:\n{previous_ctx['contextoGuia']}\n\n"
                f"Pregunta del usuario: {message}"
            )
            try:
                generation = self.bedrock.invoke(follow_up_prompt)
                return self._parse_generation(generation)
            except BedrockUnavailableError:
                logger.warning(
                    "Bedrock no disponible para seguimiento del tema %s; usando contextoResumen",
                    previous_ctx["slug"],
                )
                return self._contexto_resumen(previous_ctx["slug"])

        retrieved = self.retriever.search(message, top_k=3)
        if retrieved:
            return self._answer_from_retrieval(session_id, retrieved, message)

        self.conversation_context.pop(session_id, None)
        return NO_TOPIC_RESPONSE

    def _answer_from_retrieval(self, session_id: str, chunks: list[Chunk], message: str) -> str:
        self.conversation_context.pop(session_id, None)
        context = "\n\n".join(chunk.text for chunk in chunks)
        prompt = (
            "Eres un asistente de IntersectIA, un proyecto educativo sobre IoT, vehículos "
            "autónomos y gestión autónoma de intersecciones. Responde la pregunta del usuario "
            "basándote ÚNICAMENTE en el contexto proporcionado.\n"
            "Tu respuesta debe ser en español, clara y concisa.\n"
            'Devuelve tu respuesta en formato JSON exactamente así: {"respuesta": "texto de la respuesta"}\n\n'
            f"Contexto:\n{context}\n\n"
            f"Pregunta del usuario: {message}"
        )
        try:
            return self._parse_generation(self.bedrock.invoke(prompt))
        except BedrockUnavailableError:
            return chunks[0].text

    def _answer_with_context(self, session_id, topic, message):
        self._remember(session_id, topic)
        context = topic.get("contextoGuia", "")
        retrieved = self.retriever.search(message, top_k=2)
        if retrieved:
            context += "\n\nInformación adicional:\n" + "\n\n".join(
                chunk.text for chunk in retrieved
            )
        prompt = (
            "Eres un asistente de IntersectIA, un proyecto educativo sobre IoT y vehículos "
            "autónomos. Responde la pregunta del usuario basándote ÚNICAMENTE en el contexto "
            "proporcionado.\n"
            "Tu respuesta debe ser en español, clara y concisa.\n"
            'Devuelve tu respuesta en formato JSON exactamente así: {"respuesta": "texto de la respuesta"}\n\n'
            f"Contexto:\n{context}\n\n"
            f"Pregunta del usuario: {message}"
        )
        try:
            generation = self.bedrock.invoke(prompt)
            return self._parse_generation(generation)
        except BedrockUnavailableError:
            logger.warning(
                "Bedrock no disponible para el tema %s; degradando a contextoResumen",
                topic["slug"],
            )
            return topic.get("contextoResumen", NO_TOPIC_RESPONSE)

    def _parse_generation(self, generation: str) -> str:
        parsed = None
        try:
            parsed = json.loads(generation)
        except (json.JSONDecodeError, ValueError):
            match = re.search(r"\{[\s\S]*\}", generation)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except (json.JSONDecodeError, ValueError):
                    parsed = None
        if isinstance(parsed, dict) and isinstance(parsed.get("respuesta"), str):
            return parsed["respuesta"]
        return generation

    def _contexto_resumen(self, slug: str) -> str:
        for topic in self.topics:
            if topic["slug"] == slug:
                return topic.get("contextoResumen", NO_TOPIC_RESPONSE)
        return NO_TOPIC_RESPONSE

    def get_available_topics(self) -> list[dict]:
        return sorted(
            (
                {
                    "slug": topic["slug"],
                    "titulo": topic.get("titulo", ""),
                    "categoria": topic.get("categoria", ""),
                }
                for topic in self.topics
            ),
            key=lambda t: t["titulo"],
        )