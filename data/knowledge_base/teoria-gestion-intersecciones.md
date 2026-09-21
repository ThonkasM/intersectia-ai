# Teoría: gestión de intersecciones

## AIM: gestión autónoma de intersecciones (Dresner & Stone, 2008)

El enfoque académico que inspira a IntersectIA es *Autonomous Intersection Management* (AIM), propuesto por Kurt Dresner y Peter Stone (Journal of Artificial Intelligence Research, 31:591-656, 2008). Trata la intersección como un **agente gestor** y a cada vehículo como un **agente conductor**. En lugar de que cada vehículo decida por su cuenta, los vehículos **solicitan reservas de espacio-tiempo** (qué celdas de la intersección usarán y en qué intervalo) y el gestor las confirma, rechaza o contraoferta. Como el gestor puede emular un semáforo o un stop, **subsume** los controles actuales, y en simulación los supera en tiempo de espera y throughput cuando la penetración de vehículos autónomos es alta. IntersectIA implementa una versión simplificada basada en cola y decisión, no en celdas de reserva.

## Intersecciones sin semáforo vs semáforos

Un semáforo asigna el derecho de paso por **fases** (fijas o actuadas). Es eficiente con demanda alta y equilibrada, pero desperdicia tiempo (*idle time*) cuando hay poco tráfico o demanda desigual: los vehículos esperan con el carril contrario vacío. Los esquemas **actuados** y **adaptativos** ajustan las fases con datos de sensores, y los controladores modernos usan presión de cola (**max-pressure**, Varaiya 2013). En un semáforo, el "peor caso" es esperar un ciclo completo aunque no venga nadie por el otro eje.

## Por qué "sin semáforos" es viable con autónomos

Los semáforos existen porque los humanos no pueden negociar un cruce con seguridad a alta frecuencia. Con vehículos conectados la infraestructura conoce posición y velocidad de cada uno (V2I) y puede ordenar los cruces con márgenes de seguridad calculados, reduciendo el tiempo perdido en arranques y paradas. El límite ya no son los conductores sino el mecanismo que coordina sus acciones.
