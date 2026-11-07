"""Platform cryptographic utilities for password hashing and JWT token generation."""
from datetime import datetime, timedelta, timezone
import os
from typing import Optional

import bcrypt
import jwt

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_jwt_token(
    data: dict,
    secret_key: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encode a signed HS256 JWT access token."""
    key = secret_key or os.getenv("SECRET_KEY", "")
    expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=expire_minutes)
    )
    return jwt.encode(payload, key, algorithm=ALGORITHM)
