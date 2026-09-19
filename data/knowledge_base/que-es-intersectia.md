# IntersectIA

IntersectIA es una plataforma educativa sobre IoT y vehículos autónomos que incluye una demo 3D de una intersección de cuatro vías (Norte, Sur, Este, Oeste) donde un gestor decide qué vehículo cruza.

## Componentes

- **Frontend**: Next.js 16 con Three.js. Landing informativa más la demo 3D en `/demo`. El frontend solo renderiza e interpola posiciones; nunca decide quién cruza en los modos gestionados.
- **Backend**: NestJS con Prisma y socket.io. Es la fuente de verdad de la simulación: genera vehículos, los mueve, los encola y decide quién cruza. Tick de 50 ms (20 Hz).
- **Servicio de IA**: FastAPI. Expone `/decision` (política de cruce de baja latencia, sin LLM) y `/chat` (asistente educativo).

## Modos de simulación

- **traditional**: regla de prioridad a la derecha (Art. 52 del Código Nacional de Tránsito de Bolivia). Se simula localmente en el frontend.
- **managed**: gestor determinista FIFO (primero en llegar, primero en cruzar).
- **managed-ai**: como managed pero consulta la política de IA con un timeout de 150 ms y cae al motor determinista si falla.

## Objetivo

Demostrar cómo un gestor central puede coordinar vehículos en una intersección sin semáforos, comparando una regla local (prioridad a la derecha), un algoritmo determinista y una política entrenada, con métricas de espera y violaciones.
