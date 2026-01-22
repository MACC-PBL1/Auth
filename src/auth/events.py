from .global_vars import LISTENING_QUEUES
from .sql import (
    update_status,
    User,
)
from chassis.messaging import (
    MessageType,
    register_queue_handler,
)
from chassis.sql import SessionLocal
import logging

logger = logging.getLogger(__name__)

@register_queue_handler(LISTENING_QUEUES["compromised"])
async def piece_request(message: MessageType) -> None:
    assert (client_id := message.get("client_id")) is not None, "'client_id' should be present"

    client_id = int(client_id)

    async with SessionLocal() as db:
        await update_status(db, client_id, User.STATUS_SUSPENDED)

    logger.warning(f"[EVENT:USER:SUSPENDED] - client_id={client_id}")