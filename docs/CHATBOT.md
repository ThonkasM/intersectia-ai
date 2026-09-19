# Chatbot educativo

`POST /chat` responde en español sobre IoT, vehículos autónomos y el propio proyecto IntersectIA.

## Flujo de respuesta

1. **Match exacto** de pregunta en `data/topics.json` (normalizado, sin acentos) → respuesta directa, sin LLM.
2. **Saludos y sentimientos** → respuesta fija, sin LLM.
3. **Match por keywords** de un tema → respuesta con el `contextoGuia` del tema (más fragmentos recuperados) mediante el LLM.
4. **Retriever** sobre `data/knowledge_base/` → si hay fragmentos relevantes, responde con ellos.
5. Si nada aplica → mensaje de fallback.

Sin credenciales de AWS, degrada a `contextoResumen` (responde offline).

## Base de conocimiento

- `data/topics.json` — 14 temas con keywords, `contextoResumen`, `contextoGuia` y pares Q&A. Cubre IoT, vehículos autónomos, V2V/V2I, la demo, modos, la IA, el stack, controles, métricas, sesiones, estados, handover y problemas frecuentes.
- `data/knowledge_base/*.md` — documentos en lenguaje natural de la app. El retriever los indexa por fragmentos.

## Retriever

Implementación ligera, sin dependencias externas ni red:
- `rag/embeddings.py` — tokenización y vector Bolsa de Palabras.
- `rag/retriever.py` — fragmenta los `.md` por secciones/párrafos y puntúa con **TF-IDF**. Devuelve el top-k por encima de un umbral.

Funciona offline y es fácil de extender: basta con agregar un `.md` a `data/knowledge_base/`.

## Cómo ampliar el chatbot

1. Agrega o edita un `.md` en `data/knowledge_base/` (el retriever lo recoge al reiniciar).
2. Para respuestas exactas, agrega un par Q&A en `topics.json`.
3. Ajusta `min_score`/`top_k` en `retriever.search` si hace falta más o menos contexto.

## LLM (Bedrock)

`services/bedrock_client.py` usa boto3 con `botocore.Config` (timeouts de 2 s/10 s y 1 reintento). El prompt pide una respuesta JSON (`{"respuesta": "..."}`). Si el modelo no devuelve JSON, se usa el texto crudo. El proveedor está acoplado a la plantilla de Llama 3; cambiar de modelo requiere ajustar la plantilla.

## Mejoras futuras

- Embeddings reales (Bedrock Titan V2 u ONNX local) + índice vectorial para mejor recuperación semántica.
- Historial de conversación multi-turno y streaming de respuestas.
- Inyectar contexto vivo de la app (modo actual, métricas) desde el backend.
