# -*- coding: utf-8 -*-
"""Funciones CRUD para el microservicio de clientes."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

logger = logging.getLogger(__name__)


# CREATE ##########################################################################################
async def create_client(db: AsyncSession, client: schemas.ClientCreate):
    """Crea un cliente nuevo en la base de datos."""
    db_client = models.Client(**client.dict())
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client


# READ ############################################################################################
async def get_client(db: AsyncSession, client_id: int):
    """Obtiene un cliente por ID."""
    return await db.get(models.Client, client_id)


async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 10):
    """Lista clientes con paginación."""
    stmt = select(models.Client).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# UPDATE ##########################################################################################
async def update_client(db: AsyncSession, client_id: int, client_update: schemas.ClientUpdate):
    """Actualiza los datos de un cliente existente."""
    db_client = await get_client(db, client_id)
    if not db_client:
        return None

    update_data = client_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)

    await db.commit()
    await db.refresh(db_client)
    return db_client


# DELETE ##########################################################################################
async def delete_client(db: AsyncSession, client_id: int):
    """Elimina un cliente por ID."""
    db_client = await get_client(db, client_id)
    if db_client:
        await db.delete(db_client)
        await db.commit()
    return db_client
