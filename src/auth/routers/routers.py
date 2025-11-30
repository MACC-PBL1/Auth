from ..keys import JWTRSAProvider
from ..messaging import RABBITMQ_CONFIG
from ..sql import (
    get_user_by_id,
    get_user_by_username,
    create_user,
    LoginRequest,
    Message,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from .utils import (
    hash_password,
    verify_password,
)
from chassis.messaging import is_rabbitmq_healthy
from chassis.routers import (
    get_system_metrics,
    raise_and_log_error
)
from chassis.security import create_jwt_verifier
from chassis.sql import get_db
from fastapi import (
    APIRouter, 
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import socket

logger = logging.getLogger(__name__)
Router = APIRouter(prefix="/auth")

# ------------------------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------------------------
@Router.get(
    "/health",
    summary="Health check endpoint",
    response_model=Message,
)
async def health_check():
    if not is_rabbitmq_healthy(RABBITMQ_CONFIG):
        raise_and_log_error(
            logger=logger,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="[LOG:REST] - RabbitMQ not reachable"
        )

    _ = JWTRSAProvider(
        public_exponent=65537,
        key_size=4096,
    )
    container_id = socket.gethostname()
    logger.debug(f"[LOG:REST] - GET '/health' served by {container_id}")
    return {
        "detail": f"OK - Served by {container_id}",
        "system_metrics": get_system_metrics()
    }

@Router.get(
    "/health/auth",
    summary="Health check endpoint (JWT protected)",
    response_model=Message
)
async def health_check_auth(
    token_data: dict = Depends(create_jwt_verifier(lambda: JWTRSAProvider.get_public_key_pem(), logger))
):
    logger.debug("[LOG:REST] - GET '/health/auth' endpoint called.")

    user_id = token_data.get("sub")
    user_role = token_data.get("role")

    logger.info(f"[LOG:REST] - Valid JWT: user_id={user_id}, role={user_role}")

    return {
        "detail": f"Auth service is running. Authenticated as (id={user_id}, role={user_role})",
        "system_metrics": get_system_metrics()
    }

@Router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    maybe_user = await get_user_by_username(db, data.username)
    if maybe_user is None or not verify_password(data.password, maybe_user.hashed_password):
        raise_and_log_error(
            logger,
            status.HTTP_401_UNAUTHORIZED,
            message="[LOG:REST] - Invalid credentials"
        )
    
    assert maybe_user is not None, "User data should not be None"

    logger.info(f"[LOG:REST] - User logged in: client_id={maybe_user.id}, username={maybe_user.username}")
    
    access_token = JWTRSAProvider.create_access_token(maybe_user.id, maybe_user.role, 15)
    refresh_token = JWTRSAProvider.create_refresh_token(maybe_user.id, 7)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@Router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.debug("[LOG:REST] - GET '/refresh' endpoint called.")
    try:
        payload = JWTRSAProvider.verify_token(data.refresh_token, "refresh")
        user_id = payload["sub"]

        if (maybe_user := await get_user_by_id(db, user_id)) is None:
            raise ValueError("User does not exist")
        
        new_access = JWTRSAProvider.create_access_token(
            user_id=maybe_user.id,
            role=maybe_user.role,
            minutes=15,
        )
        new_refresh = JWTRSAProvider.create_refresh_token(
            user_id=maybe_user.id,
            days=7,
        )
        
        logger.info(f"[LOG:REST] - Refresh token created: client_id={user_id}")

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh
        )
    except ValueError as e:
        raise_and_log_error(
            logger=logger,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=f"Invalid Token: {e}",
        )

@Router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(create_jwt_verifier(lambda: JWTRSAProvider.get_public_key_pem(), logger))
):
    logger.debug("[LOG:REST] - GET '/register' endpoint called.")
    
    user_role = token_data.get("role")
    if user_role != "admin":
        raise_and_log_error(
            logger, 
            status.HTTP_401_UNAUTHORIZED, 
            f"Access denied: user_role={user_role} (admin required)",
        )

    if await get_user_by_username(db, data.username) is not None:
        raise_and_log_error(logger, status.HTTP_400_BAD_REQUEST, "Username already registered")

    new_user = await create_user(
        db,
        role=data.role,
        username=data.username,
        hashed_password=hash_password(data.password)
    )

    logger.info(
        "[LOG:REST] - User registered: ",
        f"id={new_user.id} username={new_user.username}, role={new_user.role}"
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.username,
        role=new_user.role,
    )
    

@Router.get("/key")
async def get_public_key():
    logger.debug("[LOG:REST] - GET '/key' endpoint called.")
    return {"public_key": JWTRSAProvider.get_public_key_pem()}


# TODO: MAYBE A CRUD