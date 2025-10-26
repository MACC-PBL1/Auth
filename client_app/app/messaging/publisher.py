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
    exchange_name = "public_key"

    logger.info(f"Preparando publicación en exchange '{exchange_name}'")
    logger.debug("Payload a enviar: %s", json.dumps(data, indent=2))

    try:
        with RabbitMQPublisher(
            queue="public_key_update",
            rabbitmq_config=rabbitmq_config,
            exchange=exchange_name,
            exchange_type="fanout",
        ) as publisher:
            publisher.publish(
                message=data,
            )
        logger.info(f"Public key correctamente publicado en RabbitMQ.")
    except Exception as e:
        logger.exception(f"Error publicando public key': {e}")
