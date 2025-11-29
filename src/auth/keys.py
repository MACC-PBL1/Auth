from chassis.messaging import (
    RabbitMQConfig,
    RabbitMQPublisher,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import (
    generate_private_key,
    RSAPrivateKey,
    RSAPublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
from datetime import (
    datetime, 
    timedelta, 
    timezone,
)
from pathlib import Path
from typing import Optional
import jwt
import os

__all__: list[str] = [
    "JWTRSAProvider"
]

RABBITMQ_CONFIG: RabbitMQConfig = {
    "host": os.getenv("RABBITMQ_HOST", "localhost"),
    "port": int(os.getenv("RABBITMQ_PORT", "5672")),
    "username": os.getenv("RABBITMQ_USER", "guest"),
    "password": os.getenv("RABBITMQ_PASSWD", "guest"),
    "use_tls": bool(int(os.getenv("RABBITMQ_USE_TLS", "0"))),
    "ca_cert": Path(ca_cert_path) if (ca_cert_path := os.getenv("RABBITMQ_CA_CERT_PATH", None)) is not None else None,
    "client_cert": Path(client_cert_path) if (client_cert_path := os.getenv("RABBITMQ_CLIENT_CERT_PATH", None)) is not None else None,
    "client_key": Path(client_key_path) if (client_key_path := os.getenv("RABBITMQ_CLIENT_KEY_PATH", None)) is not None else None,
    "prefetch_count": int(os.getenv("RABBITMQ_PREFETCH_COUNT", 10))
}

class JWTRSAProvider:
    _algorithm = "RS256"
    _private_key: Optional[RSAPrivateKey] = None
    _public_key: Optional[RSAPublicKey] = None

    def __init__(
        self,
        public_exponent: int = 65537,
        key_size: int = 4096,
    ) -> None:
        if JWTRSAProvider._private_key is None:
            JWTRSAProvider._private_key, JWTRSAProvider._public_key = JWTRSAProvider._generate_keys(
                public_exponent=public_exponent,
                key_size=key_size,
            )
            JWTRSAProvider.send_ready()


    @staticmethod
    def _generate_keys(
        public_exponent: int,
        key_size: int,
    ) -> tuple[RSAPrivateKey, RSAPublicKey]:
        private_key = generate_private_key(
            public_exponent=public_exponent,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def create_access_token(
        user_id: int,
        role: str,
        minutes: int, # 15
    ) -> str:
        assert JWTRSAProvider._private_key is not None, "A private key should be created before calling this function."
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
            "role": role,
            "type": "access"
        }
        return jwt.encode(
            payload=payload,
            key=JWTRSAProvider._private_key,
            algorithm=JWTRSAProvider._algorithm,
        )
    
    @staticmethod
    def create_refresh_token(
        user_id: int,
        days: int, # 7
    ) -> str:
        assert JWTRSAProvider._private_key is not None, "A private key should be created before calling this function."
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=days),
            "type": "refresh",
        }
        return jwt.encode(
            payload=payload,
            key=JWTRSAProvider._private_key,
            algorithm=JWTRSAProvider._algorithm,
        )
    
    @staticmethod
    def get_public_key_pem() -> str:
        assert JWTRSAProvider._public_key is not None, "A public key should be created before calling this function."
        pem = JWTRSAProvider._public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    @staticmethod
    def verify_token(
        token: str, 
        token_type: str = "access"
    ) -> dict:
        assert JWTRSAProvider._public_key is not None, "A public key should be created before calling this function."
        try:
            payload: dict = jwt.decode(
                token, 
                JWTRSAProvider._public_key, 
                algorithms=[JWTRSAProvider._algorithm]
            )
            if payload.get("type") != token_type:
                raise ValueError(f"Invalid token type. Expected {token_type}")
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
        
    @staticmethod
    def send_ready() -> None:
        with RabbitMQPublisher(
            queue="client.public_key.signal",
            rabbitmq_config=RABBITMQ_CONFIG,
            exchange="public_key",
            exchange_type="fanout",
        ) as publisher:
            publisher.publish(
                message={
                    "public_key": "AVAILABLE"
                },
            )
        
    