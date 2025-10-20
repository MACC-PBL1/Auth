# app/messaging/publisher.py
import aio_pika
import json
import logging

logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://user:password@rabbitmq:5672/"  # cambia por TLS 

async def publish_cert_update(public_key: str):
    """Publica un mensaje de actualización de clave pública."""
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange("auth_events", aio_pika.ExchangeType.FANOUT)
            message = aio_pika.Message(
                body=json.dumps({
                    "event": "client.public_key",   # nombre exacto del evento
                    "public_key": public_key        # contenido del mensaje
                }).encode("utf-8")
            )
            await exchange.publish(message, routing_key="")
            logger.info(" Mensaje de actualización de clave pública publicado correctamente.")
    except Exception as e:
        logger.error(f" Error publicando actualización de clave pública: {e}")
