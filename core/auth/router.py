"""
Authentication router for Local Lift application.
"""
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core.config import get_settings
from core.database.connection import get_db
from .schemas import Token, TokenData, UserCreate, UserRead, UserLogin, UserUpdate

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Settings
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plaintext password
        hashed_password: The hashed password to compare against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.auth_token_expire_minutes)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> UserRead:
    """
    Verify and decode the JWT token from Supabase to get the current user.
    
    Args:
        token: The JWT token to decode
        db: Database session
        
    Returns:
        UserRead: The current user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    from core.supabase.client import get_supabase_admin_client
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get admin client with service role for user validation
        supabase_admin = get_supabase_admin_client()
        
        # Verify the JWT token with Supabase
        # This is a bit hacky since we're setting an auth header directly
        # but it's the most reliable way to validate a token with the Supabase Python client
        supabase_admin.auth.set_auth(token)
        
        # Get the user from the token - this will throw an error if invalid
        user_response = supabase_admin.auth.get_user()
        
        if not user_response or not user_response.user:
            raise credentials_exception
            
        supabase_user = user_response.user
        
        # Extract user ID, email and app_metadata
        user_id = supabase_user.id
        email = supabase_user.email
        app_metadata = supabase_user.app_metadata or {}
        
        # Extract role and permissions from app_metadata
        role = app_metadata.get("role", "client")
        permissions = app_metadata.get("permissions", [])
        
        # Create a user object from the Supabase data
        user = UserRead(
            id=user_id,
            email=email,
            name=supabase_user.user_metadata.get("full_name", email),
            role=role,
            permissions=permissions,
            is_active=not supabase_user.banned,
        )
        
    except Exception as e:
        import logging
        logging.error(f"Token validation error: {str(e)}")
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    """
    Check if the current user is active.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        UserRead: The current active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user: The user data for registration
        db: Database session
        
    Returns:
        UserRead: The newly created user
        
    Raises:
        HTTPException: If registration fails
    """
    # This is a placeholder - in a real implementation, you would check if the user already exists
    # existing_user = db.query(User).filter(User.email == user.email).first()
    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Email already registered"
    #     )
    
    # Hash the password
    # hashed_password = get_password_hash(user.password)
    
    # Create new user in the database
    # db_user = User(
    #     email=user.email,
    #     hashed_password=hashed_password,
    #     name=user.name,
    #     role=user.role,
    #     region_id=user.region_id
    # )
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    
    # For now, we'll simulate a created user
    created_user = UserRead(
        id=1,
        email=user.email,
        name=user.name,
        role=user.role,
        region_id=user.region_id,
        permissions=["read:profile", "update:profile"]
    )
    
    return created_user


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user using Supabase and return the access/refresh tokens.
    
    Args:
        form_data: OAuth2 password request form
        db: Database session
        
    Returns:
        Token: The access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    from core.supabase.client import get_supabase_client
    
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not auth_response or not auth_response.session:
            raise auth_exception
            
        # Return the Supabase-generated tokens
        return Token(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token
        )
        
    except Exception as e:
        import logging
        logging.error(f"Login error: {str(e)}")
        raise auth_exception


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Refresh an expired access token using a Supabase refresh token.
    
    Args:
        token: The refresh token
        db: Database session
        
    Returns:
        Token: New access and refresh tokens
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    from core.supabase.client import get_supabase_client
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Refresh the token with Supabase
        auth_response = supabase.auth.refresh_session(refresh_token=token)
        
        if not auth_response or not auth_response.session:
            raise credentials_exception
            
        # Return the new Supabase-generated tokens
        return Token(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token
        )
        
    except Exception as e:
        import logging
        logging.error(f"Token refresh error: {str(e)}")
        raise credentials_exception


@router.get("/me", response_model=UserRead)
async def get_user_me(current_user: UserRead = Depends(get_current_active_user)):
    """
    Get information about the currently authenticated user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        UserRead: The current user's information
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout the current user (client-side token invalidation).
    
    Returns:
        dict: Success message
    """
    # Note: Since JWT tokens are stateless, server-side logout requires a blacklist
    # For simplicity, we're relying on the client to discard the tokens
    return {"message": "Successfully logged out"}
