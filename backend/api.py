"""
Backend API Endpoints

This module provides simple API endpoints for the LocalLift application.
These endpoints are designed for general use cases and direct database access.
"""

from fastapi import APIRouter
from core.supabase import supabase_admin_client

router = APIRouter()

@router.get("/api/leaderboard")
def get_leaderboard():
    """
    Get the global badge leaderboard with default settings.
    
    Simple endpoint that calls the badge leaderboard database function
    with default parameters (all time period, top 10 clients).
    
    Returns:
        List of ranked clients with badge statistics
    """
    result = supabase_admin_client \
        .rpc("get_badge_leaderboard") \
        .execute()

    return result.data
