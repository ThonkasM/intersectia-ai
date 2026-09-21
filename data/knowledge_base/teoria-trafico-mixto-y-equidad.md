# Teoría: tráfico mixto y equidad

## Tráfico mixto humano-autónomo

En la práctica la adopción de vehículos autónomos es **gradual**, así que durante años conviven humanos y autónomos (*mixed autonomy*). Los estudios muestran que basta una **penetración** parcial de vehículos conectados o autónomos para mejorar espera y throughput, aunque el beneficio depende de cuántos y de dónde estén. En IntersectIA, el **vehículo del jugador** representa al humano dentro del tráfico autónomo y prueba la coordinación en ese escenario mixto, incluido el *handover* cuando el humano deja de responder.

## Equidad, p95 e inanición

Minimizar el **promedio** de espera no basta: una política puede lograr un buen promedio a costa de que una dirección espere muchísimo. Por eso se miran el **p95** (la cola de la distribución) y la **equidad** entre direcciones (la brecha entre la mejor y la peor). La **inanición** (*starvation*) ocurre cuando una dirección nunca recibe el cruce; el **deadlock/livelock** es que el sistema se trabe y no avance. IntersectIA acota la inanición con un **límite de espera** (25 s) que prioriza al vehículo postergado.
