"""
Supabase Client for LocalLift CRM

This module provides a singleton Supabase client for accessing the Supabase
backend services, including authentication, database, and storage.
"""
import os
from typing import Optional
from functools import lru_cache

from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validation
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase URL and service role key must be set in environment variables "
        "(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)"
    )

@lru_cache()
def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.
    
    This function creates a Supabase client if one doesn't exist,
    or returns the existing client if it does. The @lru_cache decorator
    ensures that only one client is created.
    
    Returns:
        Client: A Supabase client instance
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get a user by email address.
    
    Args:
        email (str): The user's email address
        
    Returns:
        Optional[dict]: The user data if found, or None if not found
    """
    supabase = get_supabase_client()
    
    # Use the admin API to search for a user by email
    response = supabase.rpc(
        "get_user_by_email", 
        {"email_to_find": email}
    ).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    
    return None

def check_permission(user_id: str, permission: str) -> bool:
    """
    Check if a user has a specific permission.
    
    Args:
        user_id (str): The user ID to check
        permission (str): The permission to check for
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    supabase = get_supabase_client()
    
    # First, get the user's role
    role_response = supabase.table("user_roles").select("role").eq("user_id", user_id).execute()
    
    if not role_response.data or len(role_response.data) == 0:
        # Default to user role if not found
        role = "user"
    else:
        role = role_response.data[0]["role"]
    
    # Define permission hierarchy
    role_permissions = {
        'user': ['view_dashboard', 'edit_profile', 'view_learning'],
        'staff': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports'],
        'manager': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users'],
        'admin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs'],
        'superadmin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs']
    }
    
    # Check if user has the permission based on their role
    has_permission = permission in role_permissions.get(role, [])
    
    if has_permission:
        return True
    
    # Also check for temporary permissions
    temp_perm_response = supabase.table("temp_permissions").select("*").eq("user_id", user_id).eq("permission", permission).gt("expiry", "now()").execute()
    
    if temp_perm_response.data and len(temp_perm_response.data) > 0:
        return True
    
    return False

def log_activity(user_id: str, action: str, resource: str, details: Optional[dict] = None) -> None:
    """
    Log a user activity for audit purposes.
    
    Args:
        user_id (str): The ID of the user performing the action
        action (str): The action being performed (e.g., "create", "update", "delete")
        resource (str): The resource being acted upon (e.g., "user", "profile", "settings")
        details (Optional[dict]): Additional details about the action
    """
    supabase = get_supabase_client()
    
    log_data = {
        "user_id": user_id,
        "action": action,
        "resource": resource,
    }
    
    if details:
        log_data["details"] = details
    
    # Insert into activity log table
    supabase.table("activity_logs").insert(log_data).execute()
