from app.rag.retriever import get_retriever


def test_retriever_indexes_knowledge_base():
    retriever = get_retriever()
    assert len(retriever.chunks) > 0


def test_retriever_finds_demo_controls():
    retriever = get_retriever()
    hits = retriever.search("como controlo el gamepad en la demo")
    assert hits
    joined = " ".join(chunk.text.lower() for chunk in hits)
    assert "gamepad" in joined or "mando" in joined


def test_retriever_ignores_unrelated_query():
    retriever = get_retriever()
    assert retriever.search("xqztvqw 92") == []
