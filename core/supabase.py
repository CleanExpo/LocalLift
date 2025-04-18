"""
Supabase Client Module

This module provides Supabase client instances for database operations
and real-time functionality.
"""

import os
from typing import Optional
from supabase import create_client, Client

from core.config import get_settings

# Cached client instances
_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create a Supabase client instance with anon key.
    
    Returns:
        Client: A Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    
    return _supabase_client

def get_supabase_admin_client() -> Client:
    """
    Get or create a Supabase client instance with service role key.
    This client has admin privileges and should be used carefully.
    
    Returns:
        Client: A Supabase admin client instance
    """
    global _supabase_admin_client
    
    if _supabase_admin_client is None:
        settings = get_settings()
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not service_key:
            raise ValueError(
                "SUPABASE_SERVICE_KEY environment variable is not set. "
                "This is required for admin operations."
            )
        
        _supabase_admin_client = create_client(settings.supabase_url, service_key)
    
    return _supabase_admin_client

# Export the default client for convenience
supabase_client = get_supabase_client()
supabase_admin_client = None  # Will be initialized on first use
