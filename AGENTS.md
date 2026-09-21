# IntersectIA AI

IntersectIA AI is the FastAPI AI service for the autonomous intersection demo. It has two very
different responsibilities: a low-latency `/decision` endpoint that runs a lightweight in-memory
policy and is called by the NestJS backend once per simulation tick (budget ~150ms, and it must
NEVER use an LLM), and a `/chat` educational RAG endpoint where an LLM is allowed and latency is
relaxed.

## Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime + test (para desarrollo)
uvicorn app.main:app --reload --port 8000
pytest
```

`requirements.txt` es **solo runtime** (lo que instala la imagen Docker); `requirements-dev.txt`
agrega `pytest`/`httpx`. No agregues deps de test al runtime.

## Architectural conventions

- NEVER use an LLM on the `/decision` path — only on `/chat`.
- The policy model is loaded ONCE at process startup (module-level `_policy =
  load_trained_policy()`), never per-request.
- `/decision` must make NO network calls and no file loads per request; everything stays in memory
  from startup. Measure latency, it must stay under 150ms.
- Training (`app/policy/train.py`) runs offline, separate from the server process — it must never
  be imported or executed by `infer.py` in production.
- The RAG index/embeddings are built once lazily (module-level singleton) and reused across
  requests.
- Both endpoints are protected by `verify_internal_token` (header `X-Internal-Token`) — the AI
  service only accepts traffic from the NestJS backend, never from the browser.
- Env vars come from pydantic-settings (`app/core/config.py`) with prefix `AI_`. The settings now set
  `env_file=".env"`, so the `.env` **is loaded**; keep it in sync with `.env.example`.

## Policy / RAG conventions

- The trained artifact is **JSON** (`data/trained_policy.json`, gitignored), never `pickle` (avoids
  arbitrary-code execution on load). `load_trained_policy()` accepts `.json` or legacy `.pkl`.
- `infer(queue, occupant)` passes the occupant to the policy; accept integer responses including
  `numpy.integer` but reject `bool`.
- The chatbot retriever (`app/rag/retriever.py`) is a dependency-free TF-IDF search over
  `data/knowledge_base/*.md`. Add app knowledge by dropping a `.md` there; add exact answers in
  `data/topics.json`.
- `python -m app.policy.train` is offline, CPU-only, reproducible (fixed seed) and prints an
  evaluation vs heuristic/random. See `docs/TRAINING.md` and `docs/CHATBOT.md`.