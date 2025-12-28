from .models import User
from chassis.sql import (
    get_element_by_id,
    get_element_statement_result
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

async def create_user(
    db: AsyncSession,
    role: str,
    username: str,
    hashed_password: str
) -> User:
    new_user = User(
        role=role,
        username=username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_id(
    db: AsyncSession,
    id: int,
) -> Optional[User]:
    return await get_element_by_id(
        db,
        User,
        id
    )

async def get_user_by_username(
    db: AsyncSession,
    username: str,
) -> Optional[User]:
    return await get_element_statement_result(
        db=db,
        stmt=select(User).where(User.username == username)
    )

async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()
