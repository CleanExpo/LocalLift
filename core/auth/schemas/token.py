"""
Token schemas for authentication.
"""
from typing import Optional, List
from pydantic import BaseModel


class Token(BaseModel):
    """
    Token response model with access and refresh tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Token payload data with user information and permissions.
    """
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = []
    exp: Optional[int] = None  # Expiration timestamp
