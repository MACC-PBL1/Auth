from pydantic import (
    BaseModel,
    EmailStr,
)

class LoginRequest(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    detail: str = "Operation successful"

class RefreshRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str