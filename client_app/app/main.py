# -*- coding: utf-8 -*-
"""Main file to start FastAPI Auth Service."""
import logging.config
import os
from fastapi import FastAPI
from app.routers import main_router
from app.sql import models, database
from app.security.keys import generate_keys
from app.init_admin import init_admin

# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------
logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.ini"))
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# OpenAPI metadata
# ---------------------------------------------------------------------
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
logger.info("Running app version %s", APP_VERSION)

DESCRIPTION = """
Servicio de **autenticación** y **autorización** centralizado.  
Genera tokens **JWT (RS256)**, gestiona usuarios y roles.
"""

tags_metadata = [
    {"name": "Auth Service", "description": "Autenticación y emisión de tokens JWT."},
    {"name": "Users", "description": "Gestión de usuarios y roles."},
    {"name": "Public Key", "description": "Provee la clave pública para validar tokens."},
]

# ---------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------
app = FastAPI(
    title="Auth Service",
    description=DESCRIPTION,
    version=APP_VERSION,
    openapi_tags=tags_metadata,
)


# ---------------------------------------------------------------------
# App startup
# ---------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    """Se ejecuta al iniciar la app."""
    logger.info(" Iniciando Auth Service...")

    # Crear tablas si no existen
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        logger.info("Tablas verificadas/creadas.")

    # Generar claves RSA si no existen
    generate_keys()
    logger.info(" Claves RSA disponibles.")

    # Crear rol y usuario admin por defecto
    async with database.SessionLocal() as session:
        await init_admin(session)
        logger.info(" Usuario admin inicializado.")

    logger.info(" Auth Service iniciado correctamente.")


# ---------------------------------------------------------------------
# App shutdown
# ---------------------------------------------------------------------
@app.on_event("shutdown")
async def on_shutdown():
    """Se ejecuta al cerrar la app: libera recursos."""
    logger.info("Cerrando Auth Service...")
    await database.engine.dispose()


# ---------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------
app.include_router(main_router.router)
