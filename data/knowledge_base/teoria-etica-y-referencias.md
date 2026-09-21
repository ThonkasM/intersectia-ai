# Teoría: ética, responsabilidad y referencias

## Ética y responsabilidad

En un cruce gestionado por un árbitro central, decidir "quién pasa primero" es también una decisión **ética y legal**: ¿se optimiza el promedio y se posterga a una minoría, o se garantiza equidad? ¿Quién responde si dos autónomos colisionan? IntersectIA no resuelve estos dilemas, pero los deja visibles al exponer la **equidad** como métrica y al incluir reglas como el **límite de inanición**. Los marcos regulatorios internacionales (por ejemplo UNECE e ISO) todavía debaten la responsabilidad en función del nivel SAE.

## Fundamento teórico del proyecto — referencias

IntersectIA se apoya en cuatro pilares:

- **AIM** — Dresner, K. & Stone, P. (2008). *A Multiagent Approach to Autonomous Intersection Management*. Journal of Artificial Intelligence Research, 31:591-656.
- **V2X** — SAE J2735 (*V2X Communications Message Set Dictionary*); 3GPP C-V2X (Release 14, interfaz PC5 sidelink); DSRC IEEE 802.11p / 802.11bd.
- **Niveles de autonomía** — SAE J3016 (ISO PAS 22736).
- **Control y RL** — Varaiya (2013), *max-pressure*; surveys de aprendizaje por refuerzo para control de señales de tráfico.

Si preguntan "¿en qué teoría se basa IntersectIA?", la respuesta corta es: en el paradigma **AIM** de arbitraje central por reservas, comunicado por **V2X** y resuelto con una **política de RL** liviana.
