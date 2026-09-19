# Entrenamiento de la política

Pipeline offline y reproducible. Corre en **CPU en segundos** (no necesita GPU), tanto en una MacBook como en la nube.

## Ejecutar

```bash
cd intersectia-ai
source .venv/bin/activate
python -m app.policy.train
```

Salida: `data/trained_policy.json` y una comparación de métricas.

## Entorno de entrenamiento

`IntersectionEnv` modela una intersección con **eje ocupado**:
- Se concede el paso a un vehículo; mientras un eje (Norte-Sur o Este-Oeste) está ocupado durante `SERVICE_TIME` pasos, solo se puede conceder a vehículos del mismo eje.
- Conceder a un eje en conflicto no libera al vehículo y recibe una penalización.
- La recompensa es la espera liberada menos la penalización (shaping que hace visible el efecto de la acción).

Por eso **el orden importa**: no basta con servir siempre al que más esperó.

## Estado, acción y modelo

- **Estado**: por dirección, conteo (0–3) y espera máxima en bins; más el eje ocupado (0 = libre).
- **Acción**: posición en la cola ordenada por espera.
- **Modelo**: Q-table tabular (`QTable`) con Q-learning. Se guarda como JSON.

## Evaluación

`evaluate(policy)` corre episodios con semilla fija y reporta `total_cost`, `crossings` y `avg_cost`. La política entrenada se compara contra la heurística y contra una política aleatoria. Resultado típico:

| Política | avg_cost |
|---|---|
| Entrenada | ~6.1 |
| Aleatoria | ~7.5 |
| Heurística (mayor espera) | ~8.6 |

La política aprende a evitar concesiones conflictivas cuando la intersección está ocupada.

## Nube

El entrenamiento es determinista y sin GPU, así que puede correr en AWS Batch o SageMaker Training con una instancia CPU mínima. Recomendaciones:
- Publicar el artefacto a **S3 versionado** con `git_sha`, semilla y métricas de evaluación (manifest).
- Ejecutar la evaluación en CI y **fallar si no mejora** a la heurística.
- Mantener formato JSON/ONNX; evitar `pickle` en producción.

## Reproducibilidad

Semilla fija (`seed=0` por defecto), sin dependencias de numpy/torch. Fijar versiones con `requirements.txt`.
