"""Security utilities for password hashing and JWT token handling."""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context - using Argon2 (more secure than bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using Argon2.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: The data to encode in the token (typically {"sub": user_id})

    Returns:
        The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode

    Returns:
        The decoded token payload, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token_type(payload: dict, expected_type: str) -> bool:
    """
    Verify that a token payload has the expected type.

    Args:
        payload: The decoded token payload
        expected_type: The expected token type ("access" or "refresh")

    Returns:
        True if token type matches, False otherwise
    """
    return payload.get("type") == expected_type
