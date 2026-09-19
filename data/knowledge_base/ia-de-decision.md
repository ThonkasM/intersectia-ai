# La IA de decisión

El servicio de IA expone `POST /decision`, que el backend llama una vez por tick en el modo `managed-ai`. El presupuesto de latencia es de 150 ms y **nunca usa un LLM**: ejecuta una política en memoria.

## Política

- Si no hay una política entrenada disponible, se usa una heurística que concede el paso al vehículo que más ha esperado.
- La política entrenada es una Q-table que considera la ocupación actual de la intersección (eje Norte-Sur o Este-Oeste) además de la cola. Así aprende a no conceder el paso a un eje en conflicto con el que está ocupado, algo que la heurística no tiene en cuenta.
- El backend envía también el `occupant` (vehículo que está cruzando) para que la política pueda decidir con esa información.

## Entrenamiento

El entrenamiento es offline (`app/policy/train.py`) y reproducible con semilla fija. Corre en CPU en pocos segundos y guarda el artefacto en formato JSON (`data/trained_policy.json`), evitando los riesgos de seguridad de `pickle`.

En el escenario de evaluación, la política entrenada reduce el costo medio frente a la heurística y frente a una política aleatoria, porque evita concesiones conflictivas cuando la intersección está ocupada.

## Fallback

Si la IA no responde dentro de 150 ms, devuelve un id inválido o falla, el backend usa automáticamente el motor determinista FIFO. La simulación nunca se detiene por culpa de la IA.

## Chat

`POST /chat` es el asistente educativo. Sí puede usar un LLM (AWS Bedrock). Recupera fragmentos de esta base de conocimiento y responde en español. Sin credenciales de AWS degrada a respuestas offline con la información disponible.
