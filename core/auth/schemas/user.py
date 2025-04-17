"""
User schemas for authentication and user management.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field


class UserBase(BaseModel):
    """
    Base user schema with common attributes.
    """
    email: EmailStr
    name: str
    is_active: bool = True


class UserCreate(UserBase):
    """
    User creation schema with password.
    """
    password: str = Field(..., min_length=8)
    role: str = "client"  # Default role
    region_id: Optional[int] = None
    
    @validator("password")
    def password_strength(cls, v):
        """
        Validate password strength.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserRead(UserBase):
    """
    User information returned to clients.
    """
    id: int
    role: str
    region_id: Optional[int] = None
    permissions: List[str] = []
    
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    """
    User update schema with optional fields.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    region_id: Optional[int] = None
    
    @validator("password")
    def password_strength(cls, v):
        """
        Validate password strength if provided.
        """
        if v is None:
            return v
            
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserLogin(BaseModel):
    """
    User login schema with email and password.
    """
    email: EmailStr
    password: str
