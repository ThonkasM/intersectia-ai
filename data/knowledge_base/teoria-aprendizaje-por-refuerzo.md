# Teoría: aprendizaje por refuerzo para la decisión

## MDP: estado, acción y recompensa

Un **proceso de decisión de Markov (MDP)** modela la decisión como estado, acción y recompensa. En IntersectIA: el **estado** es la cola y quién ocupa la intersección; la **acción** es qué vehículo liberar (o ninguno); la **recompensa** penaliza el tiempo de espera acumulado y las concesiones inseguras. El objetivo del agente es maximizar la recompensa acumulada.

## Q-learning

**Q-learning** aprende una tabla `Q(estado, acción)` que estima el valor de cada acción sin conocer el modelo del entorno: se actualiza con la recompensa recibida y el mejor valor futuro (ecuación de Bellman). Es **offline y en CPU** — se entrena contra un simulador simplificado y el resultado (`data/trained_policy.json`) se carga en memoria. En el proyecto la política considera además el **ocupante** de la intersección (eje N-S o E-O), algo que una heurística greedy no captura.

## RL vs heurística y por qué no un LLM

Una **heurística** (por ejemplo, conceder el paso al que más esperó) es determinista y barata, pero no aprende. RL mejora con la experiencia y puede evitar concesiones conflictivas cuando la intersección está ocupada. Un **LLM** no se usa en esta ruta: su latencia es de segundos, incompatible con el tick de 50 ms y el presupuesto de 150 ms. La decisión y el chat son dos caminos separados del servicio de IA.
