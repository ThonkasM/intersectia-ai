# App móvil (Expo)

Además de la web, IntersectIA tiene una app móvil en **Expo (SDK 57, Expo Router)** en el repo `intersectia-mobile`. Es una app "fina": **no** hace simulación ni WebSocket; replica la *landing* y ofrece el **chatbot**. Consume el mismo backend NestJS:

- `POST ${EXPO_PUBLIC_API_URL}/ai/chat` con `{ message, sessionId }` → `{ answer }`.
- `GET ${EXPO_PUBLIC_API_URL}/ai/chat/topics` para el **bottom sheet** de temas, agrupados por categoría.

El cliente de chat es portable (`src/lib/chat/`, mismo diseño que `intersectia-frontend/lib/chat`) y la sesión es en memoria. En el emulador de Android la URL por defecto es `http://10.0.2.2:3000` (el host visto desde el emulador). No usa la ruta `/decision` ni socket.io.
