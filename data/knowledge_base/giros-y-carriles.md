# Giros, carriles y spillback

## Carriles y cambios de carril

Cada sentido tiene **dos carriles**: el exterior (marcha normal) y el interior (sobrepaso), definidos por `LANES` en `lib/constants.ts` y espejados en el backend. Si el carril propio está detenido, el vehículo inicia el cambio **antes** (`shouldChangeLaneForQueue`) usando el carril vecino libre, y al cambiar elige el carril con **menos vehículos por delante** (balanceo). En los giros, cada movimiento tiene un carril asignado (derecha → exterior, izquierda → interior) y se mantiene en los cambios.

## No bloquear la intersección (spillback)

**Spillback** es que un vehículo quede atravesado en la intersección y bloquee los movimientos en conflicto. El backend evita conceder el cruce si hay un vehículo detenido por delante en el tramo de salida (`exitBlockedBy`): en ese caso espera en la línea de parada. Además, el **ocupante se libera apenas cruza**: una dirección en conflicto deja de esperar cuando el vehículo supera el centro más un margen (`occupantHasCleared`), no cuando desaparece en el horizonte; eso reduce la espera innecesaria.

## Giros (opcional)

Los giros están **desactivados por defecto** y se activan con `setTurns` desde la UI (igual que las colisiones). Cada vehículo elige un movimiento (60% recto, 20% derecha, 20% izquierda) y sigue una **curva Bézier cuadrática** dentro de la intersección, desde su carril de entrada al de salida (derecha → carril exterior, izquierda → interior); al terminar adopta la dirección de salida y sigue recto. Los conflictos se resuelven por **movimiento** (`movementConflicts`): en un mismo acceso dos rectos por carriles paralelos son compatibles, pero cualquier giro conflictúa; en ejes opuestos recto+recto y recto+derecha no conflictúan (solo la izquierda cruza al de enfrente); los perpendiculares siempre conflictúan.
