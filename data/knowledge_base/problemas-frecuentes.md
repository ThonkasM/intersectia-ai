# Problemas frecuentes

## No se ven vehículos o el HUD dice "desconectado"

- Verifica que `NEXT_PUBLIC_WS_URL` apunte al backend, normalmente `ws://localhost:3000`.
- Comprueba que el backend esté escuchando en el puerto 3000.
- El frontend en desarrollo suele correr en el puerto 3001 para no chocar con el backend; la URL del backend sigue siendo 3000.

## Error de tabla inexistente en PostgreSQL

Si el backend registra que una tabla como `SimulationSession` no existe, faltan las migraciones de Prisma. Ejecuta `npx prisma migrate dev` en `intersectia-backend`.

## Las llamadas a la IA devuelven 403

El servicio de IA exige la cabecera `X-Internal-Token`. El token del backend (`INTERNAL_SERVICE_TOKEN`) debe coincidir con el de la IA (`AI_INTERNAL_SERVICE_TOKEN`). En desarrollo ambos son `dev-internal-token`.

## La IA responde con la heurística y no con la política entrenada

Comprueba que exista `data/trained_policy.json` y que `AI_TRAINED_POLICY_PATH` apunte a ese archivo. Si el archivo no existe, el servicio usa la heurística sin fallar.

## Todos los usuarios ven la misma simulación

No debería ocurrir: cada cliente se une a una sala por sesión. Si se observa, revisa que el frontend envíe un `sessionId` distinto en el handshake de socket.io.

## El servidor no arranca por EADDRINUSE en el puerto 3000

Hay otro proceso usando el puerto. El frontend y el backend no deben usar ambos el 3000; lanza el frontend en 3001 con `npm run dev -- -p 3001`.
