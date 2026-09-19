# Cómo usar la demo 3D

La demo está en la ruta `/demo` del frontend. Cada persona que entra obtiene su **propia sesión de simulación** aislada: las acciones de un visitante no afectan a las de otro.

## Controles

- **Ratón**: arrastrar para orbitar la cámara, rueda para acercar o alejar.
- **Clic sobre un vehículo**: lo congela o lo reanuda (solo autónomos).
- **Gamepad**: controla el vehículo del jugador.
  - Gatillos: acelerar/frenar.
  - Botones 4/5: cambiar de carril.
  - Botón X (2): alternar cámara orbital / primera persona.
  - Botón Y (3): cambiar el zoom del minimapa.

## Panel (HUD)

Muestra el modo actual, vehículos cruzados, vehículos en espera, espera promedio, estado de la conexión y del gamepad, la última decisión y si el jugador está autorizado a cruzar.

## Controles de simulación

- **setMode**: cambia entre traditional, managed y managed-ai.
- **freezeVehicle / resumeVehicle**: detiene o reanuda un vehículo autónomo.
- **reset**: reinicia la simulación de la sesión.
- **setCollisions**: activa o desactiva las colisiones entre vehículos.

## Vehículo del jugador

Cuando hay un gamepad conectado, aparece un vehículo cian controlado por el jugador. Sus posiciones se envían al backend a unos 15 Hz. Si el backend deja de recibir datos del jugador durante más de 2 segundos, el vehículo pasa a modo autónomo (handover) y termina el cruce por sí solo.
