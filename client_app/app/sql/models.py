# -*- coding: utf-8 -*-
"""Database models definitions. Table representations as class."""
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base
import bcrypt


class BaseModel(Base):
    """Base reusable table."""
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        fields = ", ".join(f"{c.name}='{getattr(self, c.name)}'" for c in self.__table__.columns)
        return f"<{self.__class__.__name__}({fields})>"


class Role(BaseModel):
    """Tabla de roles (admin, client, etc.)."""
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(150), nullable=True)

    #users = relationship("User", back_populates="role")
    users = relationship("User", back_populates="role", lazy="selectin")



class User(BaseModel):
    """Tabla de usuarios autenticables (antes Client)."""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(100), nullable=False)
    #payment = Column(Float, nullable=True)

    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relación con Role
    role_id = Column(Integer, ForeignKey("role.id"))
    #role = relationship("Role", back_populates="users")
    role = relationship("Role", back_populates="users", lazy="selectin")

    def set_password(self, password: str): #crea un hash unico que representa la contraseña y se guarda en la base de datos
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8")) #verifica si la contraseña coincide con el hash

    def has_role(self, role_name: str) -> bool:
        """Comprueba si el usuario tiene un rol concreto."""
        return self.role and self.role.name.lower() == role_name.lower()
