"""
Supabase Integration Module

This package provides Supabase integration for the LocalLift application,
including client configuration, utility functions, and database operations.
"""

from .client import (
    supabase_client, get_supabase_client,
    supabase_admin_client, get_supabase_admin_client,
    SUPABASE_URL, SUPABASE_PROJECT_ID
)
from .helpers import (
    # Auth helpers
    sign_up_user, sign_in_user, sign_out_user, get_current_user,
    # Database helpers
    fetch_data, insert_data, update_data, delete_data,
    # Storage helpers
    upload_file, get_file_url, download_file, delete_file
)

__all__ = [
    # Client objects and functions
    'supabase_client', 'get_supabase_client',
    'supabase_admin_client', 'get_supabase_admin_client',
    'SUPABASE_URL', 'SUPABASE_PROJECT_ID',
    
    # Auth helpers
    'sign_up_user', 'sign_in_user', 'sign_out_user', 'get_current_user',
    
    # Database helpers
    'fetch_data', 'insert_data', 'update_data', 'delete_data',
    
    # Storage helpers
    'upload_file', 'get_file_url', 'download_file', 'delete_file'
]
