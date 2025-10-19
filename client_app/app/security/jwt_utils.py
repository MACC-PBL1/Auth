# app/security/jwt_utils.py
import jwt
from datetime import datetime, timedelta
from app.security.keys import PRIVATE_KEY_PATH, PUBLIC_KEY_PATH

ALGORITHM = "RS256"
EXP_MINUTES = 60 #JWT expira al de 60 minutos

def create_jwt(user_id: int, username: str, role: str):
    """Create JWT signed with RS256."""
    private_key = open(PRIVATE_KEY_PATH, "r").read()
    payload = {
        "sub": str(user_id),
        "email": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=EXP_MINUTES)
    }
    return jwt.encode(payload, private_key, algorithm=ALGORITHM) #el header se genera automaticamente mediante PyJWT

def verify_jwt(token: str):
    """Verify JWT and return payload."""
    public_key = open(PUBLIC_KEY_PATH, "r").read()
    return jwt.decode(token, public_key, algorithms=[ALGORITHM])
