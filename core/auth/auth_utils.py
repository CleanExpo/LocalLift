"""
Authentication utility functions for the LocalLift application.
Used in both development and production environments.
"""

import os
import logging
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union

# Set up logging
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "development_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the provided data and expiration time.
    
    Args:
        data: Dictionary containing data to encode in the token
        expires_delta: Optional expiration time delta, defaults to JWT_EXPIRATION_MINUTES
        
    Returns:
        Encoded JWT token as a string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise

def decode_token(token: str) -> Union[Dict[str, Any], None]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token payload or None if invalid
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.PyJWTError as e:
        logger.error(f"Error decoding token: {e}")
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if the passwords match, False otherwise
    """
    # In a real implementation, this would use a proper password hashing library
    # For Railway deployment testing, we'll just use a placeholder
    return plain_password == hashed_password  # Placeholder only, should use proper hashing

def get_current_user(token: str) -> Union[Dict[str, Any], None]:
    """
    Extract and validate the current user from a JWT token.
    
    Args:
        token: The JWT token to decode and validate
        
    Returns:
        The user information from the token or None if invalid
    """
    decoded = decode_token(token)
    if decoded and "sub" in decoded:
        # In a real implementation, this might fetch the user from a database
        # For Railway deployment testing, we'll just return the decoded token
        return {
            "user_id": decoded["sub"],
            "username": decoded.get("username", "unknown"),
            "roles": decoded.get("roles", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    return None

def get_admin_user(token: str) -> Union[Dict[str, Any], None]:
    """
    Extract and validate an admin user from a JWT token.
    
    Args:
        token: The JWT token to decode and validate
        
    Returns:
        The admin user information from the token or None if invalid or not admin
    """
    user = get_current_user(token)
    if user and "roles" in user and "admin" in user["roles"]:
        return user
    return None

# Additional authentication helper functions can be added as needed
