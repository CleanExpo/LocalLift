"""
Supabase Client

This module provides a Supabase client for database operations
and real-time functionality.
"""

import os
from typing import Optional
from supabase import create_client, Client

from core.config import settings

# Cached Supabase client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create a Supabase client instance.
    
    Returns:
        Client: A Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        # Get Supabase URL and key from environment variables or settings
        supabase_url = os.getenv("SUPABASE_URL", settings.SUPABASE_URL)
        supabase_key = os.getenv("SUPABASE_KEY", settings.SUPABASE_KEY)
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase URL and key must be set in environment variables "
                "or in the application settings."
            )
        
        # Create Supabase client
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client
