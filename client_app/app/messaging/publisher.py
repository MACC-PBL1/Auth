from microservice_chassis.events import EventPublisher

import logging

logger = logging.getLogger(__name__)

publisher = EventPublisher(exchange="auth.events")

def publish_refresh_public_key(data: dict):
    temp_publisher = EventPublisher(exchange="auth.events")
    temp_publisher.connect()
    payload = {
        "event": "client.refresh_public_key",
        "data": data
    }
    temp_publisher.publish(topic="client.refresh_public_key", payload=payload)
    temp_publisher.close()  # ← cerrar conexión explícitamente
    logger.info(" Nueva clave publicada correctamente.")

