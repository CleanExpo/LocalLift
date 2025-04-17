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
    Verify and decode the JWT token to get the current user.
    
    Args:
        token: The JWT token to decode
        db: Database session
        
    Returns:
        UserRead: The current user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(
            user_id=user_id,
            email=payload.get("email"),
            role=payload.get("role"),
            permissions=payload.get("permissions", []),
            exp=payload.get("exp")
        )
    except JWTError:
        raise credentials_exception
        
    # This is a placeholder - in a real implementation, you would fetch the user from the database
    # user = db.query(User).filter(User.id == token_data.user_id).first()
    # if user is None or not user.is_active:
    #     raise credentials_exception
        
    # For now, we'll simulate a user
    user = UserRead(
        id=token_data.user_id,
        email=token_data.email or "user@example.com",
        name="Test User",
        role=token_data.role or "client",
        permissions=token_data.permissions
    )
    
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
    Authenticate a user and return an access token.
    
    Args:
        form_data: OAuth2 password request form
        db: Database session
        
    Returns:
        Token: The access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # This is a placeholder - in a real implementation, you would fetch the user from the database
    # user = db.query(User).filter(User.email == form_data.username).first()
    # if not user or not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    
    # For now, we'll simulate authentication (only allow test credentials)
    if form_data.username != "test@example.com" or form_data.password != "Test1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.auth_token_expire_minutes)
    user_data = {
        "sub": 1,  # User ID
        "email": "test@example.com",
        "role": "client",
        "permissions": ["read:profile", "update:profile"],
    }
    
    access_token = create_access_token(
        data=user_data,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(data={"sub": 1})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Refresh an expired access token using a refresh token.
    
    Args:
        token: The refresh token
        db: Database session
        
    Returns:
        Token: New access and refresh tokens
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Check if token is expired
        expiration = datetime.fromtimestamp(payload.get("exp", 0))
        if datetime.utcnow() > expiration:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # This is a placeholder - in a real implementation, you would fetch the user from the database
    # user = db.query(User).filter(User.id == user_id).first()
    # if user is None or not user.is_active:
    #     raise credentials_exception
    
    # Create new tokens
    user_data = {
        "sub": user_id,
        "email": "test@example.com",
        "role": "client",
        "permissions": ["read:profile", "update:profile"],
    }
    
    access_token = create_access_token(data=user_data)
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


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
