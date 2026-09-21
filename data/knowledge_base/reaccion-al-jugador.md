# Reacción al jugador y anti-inanición

## El jugador no congela toda la intersección

Cuando el vehículo del jugador está dentro de la intersección, **no se congela todo**: solo ceden las direcciones que **conflictúan** con él; las direcciones opuestas o sin conflicto siguen cruzando. Los autónomos además lo esquivan por el carril libre y ceden el paso al cruzarse.

## Anti-inanición (25 s)

Para que un jugador detenido no bloquee una dirección para siempre, un vehículo que espera más de `STARVATION_LIMIT_SECONDS` (**25 segundos**) se **prioriza** y puede cruzar aunque el jugador esté bloqueando su eje. Es la versión en tiempo real de la noción de *fairness*: garantizar que ninguna dirección quede inanida.
