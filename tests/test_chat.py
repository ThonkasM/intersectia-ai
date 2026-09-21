from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.bedrock_client import BedrockUnavailableError
from app.services.chat_service import ChatService

client = TestClient(app)
TOKEN = get_settings().internal_service_token


class FakeBedrock:
    def __init__(self, response: str, fail: bool = False):
        self.response = response
        self.fail = fail
        self.calls = 0

    def invoke(self, _prompt: str, **_kwargs) -> str:
        self.calls += 1
        if self.fail:
            raise BedrockUnavailableError("offline")
        return self.response


def make_service(fake: FakeBedrock) -> ChatService:
    service = ChatService()
    service.bedrock = fake
    return service


def test_exact_qa_match_no_llm():
    fake = FakeBedrock('{"respuesta": "no deberia llamarse"}')
    service = make_service(fake)
    answer = service.ask("¿Qué es IoT?")
    assert answer == "IoT es la Internet de las Cosas: la conexión de sensores y dispositivos físicos a internet para recopilar y procesar datos en tiempo real."
    assert fake.calls == 0


def test_greeting_no_llm():
    fake = FakeBedrock('{"respuesta": "no deberia llamarse"}')
    service = make_service(fake)
    answer = service.ask("hola")
    assert "Asistente de IntersectIA" in answer
    assert fake.calls == 0


def test_keyword_match_calls_bedrock_and_parses():
    fake = FakeBedrock('{"respuesta": "respuesta del llm"}')
    service = make_service(fake)
    answer = service.ask("Explícame sobre IoT")
    assert answer == "respuesta del llm"
    assert fake.calls == 1


def test_keyword_match_degrades_offline():
    fake = FakeBedrock("", fail=True)
    service = make_service(fake)
    answer = service.ask("¿Qué es una intersección gestionada?")
    assert answer.startswith("La demo permite comparar dos modos")
    assert fake.calls == 1


def test_follow_up_degrades_offline_to_guia():
    fake = FakeBedrock("", fail=True)
    service = make_service(fake)
    service.ask("¿Qué es IoT?", "s1")
    answer = service.ask("Contame mas", "s1")
    assert answer.startswith("IoT, o Internet de las Cosas, conecta")
    assert fake.calls == 1


def test_unknown_question_returns_fallback():
    fake = FakeBedrock("", fail=True)
    service = make_service(fake)
    answer = service.ask("xqztvqw 92")
    assert "no tengo información" in answer
    assert fake.calls == 0


def test_topics_endpoint_with_token():
    resp = client.get("/chat/topics", headers={"X-Internal-Token": TOKEN})
    assert resp.status_code == 200
    body = resp.json()
    assert "topics" in body
    assert len(body["topics"]) >= 8
    first = body["topics"][0]
    assert set(first.keys()) == {"slug", "titulo", "categoria"}


def test_topics_endpoint_without_token_forbidden():
    resp = client.get("/chat/topics")
    assert resp.status_code == 403


def test_chat_post_without_token_forbidden():
    resp = client.post("/chat", json={"message": "hola"})
    assert resp.status_code == 403