"""
Badge Admin API

This module provides API endpoints for the badge admin dashboard.
"""

from fastapi import APIRouter
from core.supabase.client import supabase_admin

router = APIRouter()

@router.get("/api/admin/badge-leaderboard")
def badge_leaderboard():
    """
    Get the badge leaderboard data for admin dashboard.
    
    This endpoint calls the get_admin_badge_leaderboard RPC function
    which returns badge statistics for all clients.
    
    Returns:
        List of clients with their badge statistics
    """
    result = supabase_admin.rpc("get_admin_badge_leaderboard").execute()
    return result.data


@router.get("/api/admin/badge-stats")
def badge_statistics():
    """
    Get global badge statistics for admin dashboard.
    
    Returns:
        Summary statistics about badge earning across the platform
    """
    result = supabase_admin.rpc("get_badge_statistics").execute()
    return result.data


@router.get("/api/admin/regional-performance")
def regional_performance():
    """
    Get badge performance statistics grouped by region.
    
    Returns:
        Badge statistics for each region
    """
    result = supabase_admin.rpc("get_regional_badge_stats").execute()
    return result.data
