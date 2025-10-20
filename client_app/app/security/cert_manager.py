# app/security/cert_manager.py
import logging
import asyncio
from app.security.keys import generate_keys, PUBLIC_KEY_PATH
from app.messaging.publisher import publish_cert_update

logger = logging.getLogger(__name__)

async def init_certificates():
    """Generate keys if needed and notify other microservices."""
    # Generar las claves si no existen
    generate_keys()

    # Leer la clave pública recién creada o existente
    with open(PUBLIC_KEY_PATH, "r") as f:
        public_key = f.read()

    # Notificar al resto de microservicios (RabbitMQ)
    try:
        await publish_cert_update(public_key)
        logger.info(" Public key broadcasted to other services.")
    except Exception as e:
        logger.error(f"Failed to publish public key update: {e}")
