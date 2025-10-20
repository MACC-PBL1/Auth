# -*- coding: utf-8 -*-
"""Schemas for User and Role definitions (Auth Service)."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# =====================================================
# === Mensaje genérico
# =====================================================
class Message(BaseModel):
    """Respuesta genérica de éxito/error."""
    detail: str = Field(example="Operación realizada correctamente")


# =====================================================
# === ROLES
# =====================================================
class RoleBase(BaseModel):
    """Campos comunes de un rol."""
    name: str = Field(..., example="admin")
    description: Optional[str] = Field(None, example="Administrador del sistema")


class RoleCreate(RoleBase):
    """Schema para crear un nuevo rol."""
    pass


class RoleOut(BaseModel):
    """Schema para salida de roles."""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True 


# =====================================================
# === USUARIOS
# =====================================================
class UserBase(BaseModel):
    """Campos comunes de un usuario."""
    name: str = Field(..., example="Juan Pérez")
    email: str= Field(..., example="juan@example.com")
    phone: Optional[str] = Field(None, example="+34 600 123 456")
    #payment: Optional[float] = Field(None, example=199.99)
    is_active: bool = Field(default=True, example=True)
    role: Optional[str] = Field(default="client", example="client")


class UserCreate(UserBase):
    """Schema para crear usuario (registro o POST)."""
    password: str = Field(..., min_length=8, example="MiC0ntraseñaSegura123")


class UserLogin(BaseModel):
    """Schema de login (autenticación)."""
    email: str = Field(..., example="juan@example.com")
    password: str = Field(..., example="MiC0ntraseñaSegura123")


class UserUpdate(BaseModel):
    """Schema para actualizar datos del usuario."""
    name: Optional[str] = Field(None, example="Juan Actualizado")
    phone: Optional[str] = Field(None, example="+34 700 123 456")
    #payment: Optional[float] = Field(None, example=249.99)
    password: Optional[str] = Field(None, min_length=8, example="NuevaContraseña123")
    is_active: Optional[bool] = Field(None, example=True)
    role: Optional[str] = Field(None, example="client")


class UserOut(BaseModel):
    """Respuesta al consultar o crear un usuario."""
    id: int
    name: str
    email: str
    phone: Optional[str]
   # payment: Optional[float]
    is_active: bool
    role: Optional[RoleOut]  
    creation_date: datetime

    class Config:
        from_attributes = True 


# =====================================================
# === TOKEN / JWT
# =====================================================
class TokenData(BaseModel):
    """Datos contenidos en el JWT."""
    sub: str = Field(..., example="1")  # user_id
    email: str = Field(..., example="juan@example.com")
    role: str = Field(..., example="client")
    exp: Optional[int] = None  # fecha de expiración (epoch)
