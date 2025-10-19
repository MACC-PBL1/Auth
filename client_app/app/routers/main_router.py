# -*- coding: utf-8 -*-
"""FastAPI router definitions for Auth Service."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.sql import crud, schemas
from app.dependencies import get_db
from app.security.jwt_utils import create_jwt, verify_jwt
from app.security.keys import PUBLIC_KEY_PATH

logger = logging.getLogger(__name__)


# Router con prefijo para el API Gateway
router = APIRouter(
    prefix="/auth-service",
    tags=["Auth Service"]
)

basic_auth = HTTPBasic()
bearer_auth = HTTPBearer()


# ------------------------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------------------------
@router.get(
    "/",
    summary="Health check endpoint",
    response_model=schemas.Message,
)
async def health_check():
    """Endpoint to check if the Auth Service is running."""
    logger.debug("GET '/' endpoint called.")
    return {"detail": "Auth Service OK"}


# ------------------------------------------------------------------------------------
# AUTHENTICATION (GET /auth)
# ------------------------------------------------------------------------------------
@router.get( #LOGIN
    "/auth",
    summary="Authenticate user via Basic Auth and get JWT",
    response_model=dict,
    tags=["Authentication"]
)
async def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    db: AsyncSession = Depends(get_db)
):
    print("✅ Entró en authenticate_user")
    """Authenticate a user using Basic Auth and return JWT."""
    user = await crud.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_jwt(user_id=user.id, username=user.email, role=user.role.name) #crea el token jwt que hay que enviar a los otros microservicios
    logger.info(f"User '{user.email}' authenticated successfully.")
    return {"access_token": token}


# ------------------------------------------------------------------------------------
# PUBLIC KEY (GET /public_key)
# ------------------------------------------------------------------------------------
#para que los demás servicios puedan obtener la clave pública del Auth Service y así verificar los tokens JWT firmados con la clave privada.
@router.get(
    "/public_key",
    summary="Get public key for JWT validation",
    response_model=dict,
    tags=["Public Key"]
)
async def get_public_key():
    """Return the public key used for JWT validation."""
    with open(PUBLIC_KEY_PATH, "r") as f:
        return {"public_key": f.read()}


# ------------------------------------------------------------------------------------
# USERS (REGISTER & CRUD)
# ------------------------------------------------------------------------------------
@router.post(
    "/users/register",
    summary="Register a new user (admin only)",
    response_model=schemas.UserOut,
    tags=["Users"]
)
async def register_user(
    user_data: schemas.UserCreate,
    credentials: HTTPAuthorizationCredentials = Security(bearer_auth), # token jwt para intentar crear la cuenta
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (requires admin role)."""
    payload = verify_jwt(credentials.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    user = await crud.create_user(db, user_data)
    return user


@router.get(
    "/users",
    summary="List all users (admin only)",
    response_model=List[schemas.UserOut],
    tags=["Users"]
)
async def list_users(
    credentials: HTTPAuthorizationCredentials = Security(bearer_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all users (requires admin role)."""
    payload = verify_jwt(credentials.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    return await crud.get_users(db)


@router.get(
    "/users/{user_id}",
    summary="Get a single user by ID (admin only)",
    response_model=schemas.UserOut,
    tags=["Users"]
)
async def get_user_by_id(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Security(bearer_auth),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a user by ID (requires admin role)."""
    payload = verify_jwt(credentials.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user

@router.delete(
    "/users/{user_id}",
    summary="Delete a user by ID (admin only)",
    response_model=schemas.Message,
    tags=["Users"]
)
async def delete_user(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Security(bearer_auth),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (admin only)."""
    payload = verify_jwt(credentials.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    user = await crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

    return {"detail": f"User {user.email} deleted successfully"}
