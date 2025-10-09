# -*- coding: utf-8 -*-
"""Application dependency injector."""
import logging

logger = logging.getLogger(__name__)

MY_MACHINE = None


# Database #########################################################################################
async def get_db():
    """Generates database sessions and closes them when finished."""
    from app.sql.database import SessionLocal  # pylint: disable=import-outside-toplevel
    logger.debug("Getting database SessionLocal")
    db = SessionLocal()
    try:
        yield db
        await db.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise   # <-- importantísimo: relanza el error
    finally:
        await db.close()



# asyncio.create_task(get_machine())
# asyncio.run(init_machine())
