from .global_vars import RABBITMQ_CONFIG
from chassis.logging import (
    get_logger,
    setup_rabbitmq_logging,
)
from chassis.sql import (
    Base, 
    Engine,
    SessionLocal,
)
from chassis.consul import CONSUL_CLIENT 
from contextlib import asynccontextmanager
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging.config
import os

# Configure logging ################################################################################
logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.ini"))
setup_rabbitmq_logging(
    rabbitmq_config=RABBITMQ_CONFIG,
    capture_dependencies=True,
)
logger = get_logger(__name__)

from .routers import (
    Router,
    hash_password,
)
from .sql import (
    create_user,
    get_user_by_username,
)

# Create admin user
async def create_admin(
    db: AsyncSession,
    username: str = "admin@mondragon.edu"
) -> None:
    if await get_user_by_username(db, username) is not None:
        return
    await create_user(
        db=db,
        role="admin",
        username=username,
        hashed_password=hash_password("admin"),
    )

# App Lifespan #####################################################################################
@asynccontextmanager
async def lifespan(__app: FastAPI):
    """Lifespan context manager."""
    try:
        logger.info("[LOG:AUTH] - Starting up")
        try:
            logger.info("[LOG:AUTH] - Creating database tables")
            async with Engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("[LOG:AUTH] - Creating default admin.")
            async with SessionLocal() as db:
                await create_admin(db)
        except Exception:
            logger.error("[LOG:AUTH] - Could not create tables at startup")
        logger.info("[LOG:AUTH] - Registering service to Consul...")
        try:
            CONSUL_CLIENT.register_service(
                service_name="auth",
                ec2_address=os.getenv("HOST_IP", "localhost"),
                service_port=int(os.getenv("HOST_PORT", 80)),
            )
        except Exception as e:
            logger.error(f"[LOG:AUTH] - Failed to register with Consul: Reason={e}", exc_info=True)
        yield
    finally:
        logger.info("[LOG:AUTH] - Shutting down database")
        CONSUL_CLIENT.deregister_service()
        await Engine.dispose()

# OpenAPI Documentation ############################################################################
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
logger.info("[LOG:AUTH] - Running app version %s", APP_VERSION)
DESCRIPTION = """
Auth microservice
"""

tag_metadata = [
    {
        "name": "Auth",
        "description": "Endpoints related to auth",
    },
]

APP = FastAPI(
    redoc_url=None,
    title="FastAPI - Auth app",
    description=DESCRIPTION,
    version=APP_VERSION,
    servers=[{"url": "/", "description": "Development"}],
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/",
    },
    openapi_tags=tag_metadata,
    lifespan=lifespan,
)

APP.include_router(Router)

def start_server():
    ## Run here
    config = Config()

    config.bind = [os.getenv("HOST", "0.0.0.0") + ":" + os.getenv("PORT", "8000")]
    config.workers = int(os.getenv("WORKERS", "1"))

    logger.info("[LOG:AUTH] - Starting Hypercorn server on %s", config.bind)

    asyncio.run(serve(APP, config)) # type: ignore