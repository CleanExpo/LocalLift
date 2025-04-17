"""
Configuration settings for LocalLift application.
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseModel):
    """
    Application settings class.
    """
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    secret_key: str = "your-secret-key-here"  # Required field

    # Database Settings
    database_url: str = "sqlite:///./localdb.sqlite"

    # Supabase Settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000"]

    # Environment
    environment: str = "development"

    # Feature Flags
    enable_gamification: bool = True
    enable_leaderboards: bool = True
    enable_certifications: bool = True

    class Config:
        """
        Pydantic config class.
        """
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()
