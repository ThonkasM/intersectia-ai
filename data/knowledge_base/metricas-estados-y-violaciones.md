# Métricas, estados y violaciones

## Estados de un vehículo

- **approach**: se aproxima a la intersección.
- **queued**: detenido en la línea de parada, esperando autorización.
- **crossing**: autorizado a cruzar.
- **success**: ya despejó la intersección y se aleja.
- **gone**: salió de la escena; se registra el cruce.
- **frozen**: detenido manualmente por un usuario.
- **crashed**: colisionó (solo si las colisiones están activadas).

## Endpoints de métricas del backend

- `GET /metrics/avg?mode=managed` devuelve `{ avgWaitSeconds, total }` para un modo.
- `GET /metrics/summary` devuelve `{ totalCrossings, totalViolations, avgWaitByMode }`.

La espera promedio se calcula sobre los cruces registrados en la base de datos PostgreSQL.

## Violaciones de intersección

Si el vehículo del jugador entra a la zona de la intersección sin haber sido autorizado, el backend registra un `IntersectionViolation` (una vez por vehículo por cruce). El frontend aplica una asistencia de frenado, pero si el jugador la ignora la violación queda registrada y se refleja en `totalViolations`.

## Persistencia

El backend guarda sesiones de simulación, cruces de vehículos, violaciones y mensajes de contacto en PostgreSQL mediante Prisma. Las escrituras se hacen de forma asíncrona para no bloquear el tick de simulación.
