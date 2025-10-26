#from microservice_chassis.events import EventPublisher
import json
import logging

logger = logging.getLogger(__name__)

#publisher = EventPublisher(exchange="auth.events")


import json
import logging
from chassis.messaging.publisher import RabbitMQPublisher
from chassis.messaging.types import RabbitMQConfig

logger = logging.getLogger(__name__)


rabbitmq_config: RabbitMQConfig = {
    "host": "rabbitmq",
    "port": 5671,
    "username": "guest",
    "password": "guest",
    "use_tls": True,  
    "ca_cert": "/etc/rabbitmq/ssl/ca_cert.pem",
    "client_cert": "/etc/rabbitmq/ssl/client_cert.pem",
    "client_key": "/etc/rabbitmq/ssl/client_key.pem",
    "prefetch_count": 1,
}

def publish_refresh_public_key(data: dict) -> None:
    """Publica un evento indicando que la clave pública ha sido actualizada."""
    exchange_name = "auth.events"
    routing_key = "client.refresh_public_key"
    payload = {
        "event": routing_key,
        "data": data,
    }

    logger.info(f"Preparando publicación de evento '{routing_key}' en exchange '{exchange_name}'")
    logger.debug("Payload a enviar: %s", json.dumps(payload, indent=2))

    try:
        with RabbitMQPublisher(
            queue=routing_key,
            rabbitmq_config=rabbitmq_config,
        ) as publisher:
 
            publisher._channel.exchange_declare(
                exchange=exchange_name,
                exchange_type="topic",
                durable=True
            )

            publisher.publish(
                message=payload,
                routing_key=routing_key,
                exchange=exchange_name,
            )

        logger.info(f"Evento '{routing_key}' publicado correctamente en RabbitMQ.")
    except Exception as e:
        logger.exception(f"Error publicando evento '{routing_key}': {e}")
