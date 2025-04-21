"""
Authentication API for LocalLift CRM

This module implements authentication endpoints for the LocalLift CRM system,
including login, registration, token refresh, and password reset functionality.
"""
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext

# Import the Supabase client
from ..core.supabase.client import get_supabase_client

# Define API router
router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Default to 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Default to 7 days

# Models
class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # Subject (user ID)
    role: str = "user"  # User role, default to regular user
    exp: Optional[int] = None  # Expiration timestamp
    
class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    name: str
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Could add more complex validation (uppercase, lowercase, numbers, etc.)
        return v

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str
    
class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr
    
class PasswordReset(BaseModel):
    """Password reset model"""
    token: str
    password: str
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Could add more complex validation
        return v

# Helper functions
def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(
    subject: str, role: str, expires_delta: timedelta, token_type: str = "access"
) -> str:
    """Create JWT token with specified expiration"""
    now = datetime.utcnow()
    expires = now + expires_delta
    
    to_encode = {
        "sub": subject,
        "role": role,
        "exp": expires.timestamp(),
        "iat": now.timestamp(),
        "type": token_type
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(subject: str, role: str) -> tuple[str, int]:
    """Create access token with standard expiration"""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_token(subject, role, expires_delta, "access")
    return token, int(expires_delta.total_seconds())

def create_refresh_token(subject: str, role: str) -> str:
    """Create refresh token with extended expiration"""
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(subject, role, expires_delta, "refresh")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_payload = TokenPayload(**payload)
        
        # Check token expiration
        if token_payload.exp is None or token_payload.exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user from Supabase
        supabase = get_supabase_client()
        user_response = supabase.auth.admin.get_user_by_id(token_payload.sub)
        
        if user_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user role from user_roles table
        role_response = supabase.table("user_roles").select("role").eq("user_id", token_payload.sub).execute()
        
        user_data = user_response.user.model_dump()
        
        # Add role to user data
        if role_response.data and len(role_response.data) > 0:
            user_data["role"] = role_response.data[0]["role"]
        else:
            # Default to "user" role if not found
            user_data["role"] = "user"
            
        return user_data
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Routes
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint that returns access and refresh tokens"""
    # Authenticate with Supabase
    supabase = get_supabase_client()
    
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        # Get user info
        user = auth_response.user
        
        # Get user role from user_roles table
        role_response = supabase.table("user_roles").select("role").eq("user_id", user.id).execute()
        
        # Default to "user" role if not found
        role = "user"
        if role_response.data and len(role_response.data) > 0:
            role = role_response.data[0]["role"]
            
        # Create tokens
        access_token, expires_in = create_access_token(user.id, role)
        refresh_token = create_refresh_token(user.id, role)
        
        # Prepare user data for response
        user_data = user.model_dump()
        user_data["role"] = role
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user": user_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    supabase = get_supabase_client()
    
    try:
        # Sign up user with Supabase
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "name": user_data.name
                }
            }
        })
        
        # Get user info
        user = auth_response.user
        
        # Initialize user_roles record
        supabase.table("user_roles").insert({
            "user_id": user.id,
            "role": "user"  # Default role
        }).execute()
        
        # Create tokens
        access_token, expires_in = create_access_token(user.id, "user")
        refresh_token = create_refresh_token(user.id, "user")
        
        # Prepare user data for response
        user_response = user.model_dump()
        user_response["role"] = "user"
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user": user_response
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}",
        )

@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(request: Request):
    """Refresh access token using refresh token"""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication method",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = auth_header.replace("Bearer ", "")
        
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type and expiration
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_payload = TokenPayload(**payload)
        
        if token_payload.exp is None or token_payload.exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user from Supabase
        supabase = get_supabase_client()
        user_response = supabase.auth.admin.get_user_by_id(token_payload.sub)
        
        if user_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user role
        role = token_payload.role
        
        # Create new tokens
        access_token, expires_in = create_access_token(token_payload.sub, role)
        new_refresh_token = create_refresh_token(token_payload.sub, role)
        
        # Prepare user data for response
        user_data = user_response.user.model_dump()
        user_data["role"] = role
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user": user_data
        }
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/password-reset")
async def request_password_reset(request_data: PasswordResetRequest):
    """Request password reset"""
    supabase = get_supabase_client()
    
    try:
        # Request password reset with Supabase
        supabase.auth.reset_password_email(request_data.email)
        
        return {"message": "Password reset email sent"}
        
    except Exception as e:
        # We don't want to expose whether an email exists or not
        # for security reasons, so always return success
        return {"message": "If the email exists, a password reset link has been sent"}

@router.put("/password-reset/{reset_token}")
async def reset_password(reset_token: str, password_data: PasswordReset):
    """Reset password using reset token"""
    supabase = get_supabase_client()
    
    try:
        # Update user password
        supabase.auth.verify_otp({
            "token": reset_token,
            "type": "recovery",
            "new_password": password_data.password
        })
        
        return {"message": "Password has been reset successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

@router.post("/logout")
async def logout(request: Request):
    """Logout endpoint that invalidates the current session"""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication method",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = auth_header.replace("Bearer ", "")
        
        # Sign out with Supabase
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        # Always return success to avoid leaking information
        return {"message": "Logged out successfully"}

@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return current_user
