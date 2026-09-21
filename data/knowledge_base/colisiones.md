# Colisiones

Las colisiones son **opcionales** y se activan con `setCollisions` desde el panel de la demo. Cuando están activas, el backend detecta solapamientos entre vehículos y marca el estado **crashed**: el vehículo involucrado deja de moverse con normalidad y se refleja en la escena. Con las colisiones desactivadas (por defecto), los vehículos se coordinan sin tocarse aunque compartan la intersección. Las banderas `frozen` y `crashed` viajan en el snapshot `state` (`RemoteVehicleDto`) además del estado de cada vehículo.
