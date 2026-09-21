# Teoría: comunicación V2X y niveles de autonomía

## Taxonomía V2X

V2X (*vehicle-to-everything*) agrupa: **V2V** vehículo-vehículo, **V2I** vehículo-infraestructura, **V2P** vehículo-peatón y **V2N** vehículo-red. IntersectIA usa V2V para el estado compartido entre vehículos y V2I para que el nodo central (el gestor) coordine el cruce.

## C-V2X vs DSRC

Dos familias de radio compiten por el espectro de 5.9 GHz dedicado a transporte inteligente:

- **DSRC / ITS-G5** — basado en Wi-Fi; su capa física y MAC es IEEE **802.11p**, con evolución **802.11bd**.
- **C-V2X** — de 3GPP (Release 14 en adelante). Usa un enlace directo **PC5 sidelink** para V2V/V2I (baja latencia) y la red celular (LTE/5G NR) para V2N.

Ambas apuntan a latencias de decenas de milisegundos para aplicaciones de seguridad. Los mensajes periódicos de estado del vehículo se estandarizan en SAE **J2735**, que define el **BSM** (*Basic Safety Message*). En IntersectIA no hay radio real: el equivalente son los eventos de socket.io (`state`, `playerState`) y el proxy HTTP interno.

## SAE J3016 en detalle

La norma SAE **J3016** (ISO PAS 22736) define seis niveles según quién ejecuta la **tarea dinámica de conducción (DDT)** y su **fallback**, dentro de un **ODD** (dominio de diseño operacional). La diferencia clave está entre **L3** y **L4**: en L3 el sistema conduce pero **pide al humano que retome** cuando lo requiere; en L4 el sistema resuelve el fallback **sin intervención humana** dentro de su ODD. Por eso L4 puede prescindir del volante y L3 no. L5 es L4 sin restricción de ODD.
