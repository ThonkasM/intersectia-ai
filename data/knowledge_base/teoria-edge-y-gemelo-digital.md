# Teoría: edge computing y gemelo digital

## Edge / MEC y latencia

El **edge computing** (y su versión de red, **MEC**, *Multi-access Edge Computing*) procesa los datos cerca de su origen para reducir la latencia frente a la nube. En una intersección la decisión debe llegar en decenas de milisegundos: por eso el **gestor corre junto a la simulación** y no en la nube. El ciclo de control es **percibir → decidir → actuar**; cada etapa suma latencia y el presupuesto total del proyecto es de **150 ms** para la decisión de cruce. El chatbot, que no está en la ruta crítica, sí puede permitirse un LLM.

## Gemelo digital y simulación determinista

Un **gemelo digital** es una réplica virtual de un sistema físico. El backend de IntersectIA actúa como un gemelo digital ligero: simula el paso de vehículos de forma **determinista** y **reproducible** (misma entrada, misma salida). Esto permite generar **datasets de métricas** (esperas, cruces, violaciones) y comparar políticas en igualdad de condiciones. En el entrenamiento del agente se fija una **semilla** para que los experimentos sean reproducibles.
