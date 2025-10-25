from microservice_chassis.events import EventPublisher
import json
import logging

logger = logging.getLogger(__name__)

publisher = EventPublisher(exchange="auth.events")

def publish_refresh_public_key(data: dict):
    """Publica un evento indicando que la clave pública ha sido actualizada."""
    exchange_name = "auth.events"
    routing_key = "client.refresh_public_key"
    payload = {
        "event": routing_key,
        "data": data
    }

    logger.info("Preparando publicación de evento '%s' en exchange '%s'", routing_key, exchange_name)
    logger.debug(" Payload a enviar: %s", json.dumps(payload, indent=2))

    temp_publisher = EventPublisher(exchange=exchange_name)

    try:
        temp_publisher.connect()
        logger.info("Conexión establecida con RabbitMQ (exchange=%s)", exchange_name)

        temp_publisher.publish(topic=routing_key, payload=payload)
        logger.info(" Evento '%s' publicado correctamente en RabbitMQ.", routing_key)

    except Exception as e:
        logger.exception(" Error publicando evento '%s': %s", routing_key, e)

    finally:
        temp_publisher.close()
        logger.debug(" Conexión cerrada con RabbitMQ.")