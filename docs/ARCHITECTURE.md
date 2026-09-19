# Arquitectura del servicio de IA

FastAPI. Dos responsabilidades muy distintas:

- `POST /decision` — política de cruce de **baja latencia** (presupuesto 150 ms) llamada por el backend cada tick. **Nunca usa un LLM.**
- `POST /chat` — asistente educativo con RAG; **sí** puede usar un LLM (AWS Bedrock).

Ambos endpoints requieren la cabecera `X-Internal-Token` (el servicio solo acepta tráfico del backend).

## Estructura

```
app/
├── main.py              create_app(), /health
├── core/config.py       Settings (pydantic-settings, prefijo AI_, .env)
├── core/security.py     verify_internal_token (compare_digest)
├── api/decision.py      POST /decision
├── api/chat.py          POST /chat, GET /chat/topics
├── models/schemas.py    DTOs Pydantic
├── services/            decision_service, chat_service, bedrock_client
├── policy/              model (HeuristicPolicy, QTable), infer, train
└── rag/                 loader, embeddings, retriever
data/
├── topics.json          base de temas (keywords + Q&A)
├── knowledge_base/*.md  documentos de la app para el retriever
└── trained_policy.json  artefacto de la política (gitignored)
```

## Decisión

- La política se carga **una sola vez** al arrancar (`infer._policy`), nunca por request.
- `infer(queue, occupant)` intenta la política entrenada y, si falla o no hay artefacto, usa la heurística (mayor espera).
- Acepta como respuesta un índice entero (incluido `numpy.integer`) o un id de vehículo; rechaza `bool`.
- El artefacto se guarda en **JSON** (no `pickle`), evitando ejecución arbitraria al cargar.

## Configuración

`Settings` usa prefijo `AI_` y carga `.env` (`env_file`). Variables: `AI_INTERNAL_SERVICE_TOKEN`, `AI_TRAINED_POLICY_PATH`, `AI_BEDROCK_MODEL_ID`, `AI_AWS_REGION`, `AI_TOPICS_PATH`.

## Despliegue

`Dockerfile` multi-etapa simple, usuario no-root y `HEALTHCHECK` contra `/health`. En AWS corre como contenedor sidecar junto al backend (accesible por `localhost:8000`).
