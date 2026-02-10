"""Token schemas for authentication."""
from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str  # Subject (user ID)
    exp: int  # Expiration timestamp
    type: str  # Token type ("access" or "refresh")


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing tokens."""

    refresh_token: str
