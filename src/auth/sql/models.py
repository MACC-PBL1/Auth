from chassis.sql import BaseModel
from enum import Enum
from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)