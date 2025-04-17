"""
Backend API Endpoints

This module provides simple API endpoints for the LocalLift application.
These endpoints are designed for general use cases and direct database access.
"""

from fastapi import APIRouter, Query
from core.supabase import supabase_admin_client
from typing import Optional

router = APIRouter()

@router.get("/api/health")
def health_check():
    """
    Simple health check endpoint.

    Returns:
        Status message indicating the API is operational
    """
    return {"status": "OK", "message": "API is operational"}

@router.get("/api/leaderboard")
def get_leaderboard():
    """
    Get the global badge leaderboard with default settings.

    Simple endpoint that calls the comprehensive badge leaderboard database function
    with default parameters (all time period top 10 clients).

    Returns:
        List of ranked clients with detailed badge statistics
    """
    result = supabase_admin_client \
        .rpc("get_badge_leaderboard") \
        .execute()

    return result.data

@router.get("/api/simple-leaderboard")
def get_simple_leaderboard():
    """
    Get a simplified badge leaderboard.

    This endpoint provides a basic leaderboard showing only client names
    and badge counts sorted by total badges earned.

    Returns:
        List of clients ranked by total badges earned
    """
    result = supabase_admin_client \
        .rpc("get_simple_badge_leaderboard") \
        .execute()

    return result.data

@router.get("/api/simple-leaderboard/{timeframe}")
def get_simple_leaderboard_by_timeframe(
    timeframe: str = Query(..., description="Time period for leaderboard: 'week', 'month', 'quarter', 'year', 'all'")
):
    """
    Get a simplified badge leaderboard for a specific timeframe.

    This endpoint provides a basic leaderboard showing only client names
    and badge counts filtered by the specified time period.

    Args:
        timeframe: The time period to filter results by

    Returns:
        List of clients ranked by badges earned in the timeframe
    """
    if timeframe not in ["week", "month", "quarter", "year", "all"]:
        timeframe = "all"

    result = supabase_admin_client \
        .rpc(
            "get_simple_badge_leaderboard_time_limited",
            {"timeframe": timeframe}
        ) \
        .execute()

    return result.data
