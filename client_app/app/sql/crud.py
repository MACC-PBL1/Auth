# -*- coding: utf-8 -*-
"""Funciones CRUD para el servicio de autenticación (Users y Roles)."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from . import models, schemas

from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


# ================================================================================================
# ROLES
# ================================================================================================
async def create_role(db: AsyncSession, role: schemas.RoleCreate):
    """Crea un nuevo rol en la base de datos."""
    try:
        db_role = models.Role(name=role.name, description=role.description)
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
        logger.info(f"Rol creado: {db_role.name}")
        return db_role
    except IntegrityError:
        await db.rollback()
        logger.warning(f"Intento de crear rol duplicado: {role.name}")
        raise ValueError("Ya existe un rol con ese nombre.")


async def get_role_by_name(db: AsyncSession, name: str):
    """Obtiene un rol por su nombre."""
    stmt = select(models.Role).where(models.Role.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()


# ================================================================================================
# USERS
# ================================================================================================
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """Crea un nuevo usuario con contraseña hasheada y rol asignado."""
    try:
        # Buscar rol (por defecto 'client')
        role = await get_role_by_name(db, user.role or "client") #si el usuario no especifica rol se le pone el de cliente
        if not role:
            raise ValueError(f"El rol '{user.role}' no existe.")

        db_user = models.User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            #payment=user.payment,
            is_active=True,
            role_id=role.id,
        )
        db_user.set_password(user.password)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user) 
        stmt = select(models.User).options(selectinload(models.User.role)).where(models.User.id == db_user.id) #carga el rol para devolverlo
        result = await db.execute(stmt)
        db_user = result.scalars().first()
        logger.info(f"Usuario creado: {db_user.email}")
        return db_user
    except IntegrityError:
        await db.rollback()
        logger.warning(f"Intento de crear usuario duplicado: {user.email}")
        raise ValueError("Ya existe un usuario con ese email.")


async def get_user(db: AsyncSession, user_id: int):
    """Obtiene un usuario por ID."""
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):
    """Obtiene un usuario por su email (útil para login)."""
    stmt = (
    select(models.User)
    .options(selectinload(models.User.role))
    .where(models.User.email == email)
    )
    result = await db.execute(stmt)
    return result.scalars().first()



async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    """Lista usuarios con paginación, cargando también sus roles."""
    stmt = (
        select(models.User)
        .options(selectinload(models.User.role))  # 🔹 Carga anticipada del rol
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


# ================================================================================================
# UPDATE
# ================================================================================================
async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    """Actualiza los datos de un usuario existente."""
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)

    # Si se cambia la contraseña
    if "password" in update_data:
        db_user.set_password(update_data.pop("password"))

    # Si se cambia el rol
    if "role" in update_data and update_data["role"]:
        role = await get_role_by_name(db, update_data.pop("role"))
        if role:
            db_user.role_id = role.id

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    logger.info(f"Usuario actualizado: {db_user.email}")
    return db_user


# ================================================================================================
# DELETE USER
# ================================================================================================
async def delete_user(db: AsyncSession, user_id: int):
    """Elimina un usuario por su ID."""
    try:
        # Buscar el usuario en la base de datos
        db_user = await get_user(db, user_id)

        # Si no existe, devolver None
        if not db_user:
            logger.warning(f"Intento de eliminar usuario inexistente: ID={user_id}")
            return None

        # Eliminar el usuario
        await db.delete(db_user)
        await db.commit()

        logger.info(f"Usuario eliminado: {db_user.email}")
        return db_user  # opcional, puedes devolver un mensaje o el usuario borrado
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al eliminar usuario ID={user_id}: {str(e)}")
        raise



# ================================================================================================
# AUTHENTICATE
# ================================================================================================
async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Autentica un usuario verificando su contraseña."""
    db_user = await get_user_by_email(db, email)
    if not db_user:
        return None
    if not db_user.verify_password(password):
        return None
    if not db_user.is_active:
        return None
    return db_user
