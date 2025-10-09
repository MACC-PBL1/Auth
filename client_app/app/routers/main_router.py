# -*- coding: utf-8 -*-
"""FastAPI router definitions for Client Service."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.sql import crud, schemas
from app.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# Router con prefijo para el API Gateway
router = APIRouter(
    prefix="/client-service",   # todas las rutas estarán bajo este prefijo
    tags=["Client Service"]
)
# ------------------------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------------------------
@router.get(
    "/",
    summary="Health check endpoint",
    response_model=schemas.Message,
)
async def health_check():
    """Endpoint to check if the Client Service is running."""
    logger.debug("GET '/' endpoint called.")
    return {"detail": "OK"}


# ------------------------------------------------------------------------------------
# Clients
# ------------------------------------------------------------------------------------
@router.post(
    "/clients",
    response_model=schemas.ClientOut,
    summary="Create new client",
    status_code=status.HTTP_201_CREATED,
    tags=["Client"]
)
async def create_client(
    client: schemas.ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new client."""
    """ Devuelve el id"""
    logger.debug("POST '/clients' endpoint called.")
    return await crud.create_client(db, client)


@router.get(
    "/clients",
    response_model=List[schemas.ClientOut],
    summary="Retrieve client list",
    tags=["Client", "List"]
)
async def get_client_list(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Retrieve all clients with pagination."""
    logger.debug("GET '/clients' endpoint called.")
    return await crud.get_clients(db, skip=skip, limit=limit)


@router.get(
    "/clients/{client_id}",
    response_model=schemas.ClientOut,
    summary="Retrieve single client by id",
    tags=["Client"]
)
async def get_single_client(
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a single client by id."""
    logger.debug("GET '/clients/%i' endpoint called.", client_id)
    client = await crud.get_client(db, client_id)
    if not client:
        return {"detail": f"Client {client_id} not found"}
    return client


@router.put(
    "/clients/{client_id}",
    response_model=schemas.ClientOut,
    summary="Update client by id",
    tags=["Client"]
)
async def update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing client by id."""
    logger.debug("PUT '/clients/%i' endpoint called.", client_id)
    client = await crud.update_client(db, client_id, client_update)
    if not client:
        return {"detail": f"Client {client_id} not found"}
    return client


@router.delete(
    "/clients/{client_id}",
    summary="Delete client",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Message,
            "description": "Client successfully deleted."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message,
            "description": "Client not found"
        }
    },
    tags=["Client"]
)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a client by id."""
    logger.debug("DELETE '/clients/%i' endpoint called.", client_id)
    client = await crud.delete_client(db, client_id)
    if not client:
        return {"detail": f"Client {client_id} not found"}
    return {"detail": f"Client {client_id} deleted"}
