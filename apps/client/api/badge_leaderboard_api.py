"""
Badge Leaderboard API

This module provides endpoints for retrieving client badge leaderboards,
allowing clients to see top performers based on badge earning metrics.
"""

from fastapi import APIRouter, Query
from core.supabase import supabase_admin_client
from typing import Optional, List, Dict, Any

router = APIRouter()

@router.get("/api/leaderboard")
async def get_leaderboard(
    timeframe: Optional[str] = Query("all", description="Time period for leaderboard: 'week', 'month', 'quarter', 'year', 'all'"),
    limit: Optional[int] = Query(10, description="Number of clients to include in leaderboard", ge=1, le=100)
):
    """
    Get the badge leaderboard showing top-performing clients.
    
    This endpoint uses a database function for efficient calculation of
    badge statistics and leaderboard rankings.
    
    Args:
        timeframe: Time period for the leaderboard
        limit: Number of clients to include in the results
        
    Returns:
        A ranked list of clients with badge statistics
    """
    # Call the database function using RPC
    result = supabase_admin_client \
        .rpc(
            "get_badge_leaderboard", 
            {
                "timeframe": timeframe,
                "limit_count": limit
            }
        ) \
        .execute()

    # Return the leaderboard data
    return result.data


@router.get("/api/leaderboard/region/{region}")
async def get_region_leaderboard(
    region: str,
    timeframe: Optional[str] = Query("all", description="Time period for leaderboard: 'week', 'month', 'quarter', 'year', 'all'"),
    limit: Optional[int] = Query(10, description="Number of clients to include in leaderboard", ge=1, le=50)
):
    """
    Get the badge leaderboard for a specific region.
    
    Args:
        region: The region name to filter by
        timeframe: Time period for the leaderboard
        limit: Number of clients to include in the results
        
    Returns:
        A ranked list of clients within the specified region
    """
    # First get all leaderboard entries (with a higher limit)
    all_entries = supabase_admin_client \
        .rpc(
            "get_badge_leaderboard", 
            {
                "timeframe": timeframe,
                "limit_count": 100  # Get more entries to filter by region
            }
        ) \
        .execute()
    
    # Filter by region and apply the limit
    region_entries = [
        entry for entry in all_entries.data
        if entry["region"] and entry["region"].lower() == region.lower()
    ][:limit]
    
    # Re-rank the entries for the region
    for i, entry in enumerate(region_entries):
        entry["region_rank"] = i + 1
    
    return region_entries


@router.get("/api/leaderboard/client/{client_id}/rank")
async def get_client_rank(
    client_id: str,
    timeframe: Optional[str] = Query("all", description="Time period for rank calculation")
):
    """
    Get a specific client's rank and statistics.
    
    Args:
        client_id: The unique identifier for the client
        timeframe: Time period for the rank calculation
        
    Returns:
        The client's rank and badge statistics
    """
    # Get the full leaderboard (with a high limit to ensure we capture this client)
    all_entries = supabase_admin_client \
        .rpc(
            "get_badge_leaderboard", 
            {
                "timeframe": timeframe,
                "limit_count": 1000  # High limit to ensure we capture the client
            }
        ) \
        .execute()
    
    # Find the client in the results
    client_entry = next(
        (entry for entry in all_entries.data if entry["client_id"] == client_id),
        None
    )
    
    if not client_entry:
        # If client not found, get their basic info and return unranked data
        client_info = supabase_admin_client \
            .from_("clients") \
            .select("id, name, region") \
            .eq("id", client_id) \
            .single() \
            .execute()
        
        if client_info.data:
            return {
                "client_id": client_id,
                "client_name": client_info.data.get("name", "Unknown"),
                "region": client_info.data.get("region", "Unknown"),
                "rank": None,
                "badges_earned": 0,
                "compliance_rate": 0,
                "total_weeks": 0,
                "ranked": False,
                "message": "Client has no badge history in the specified timeframe"
            }
        else:
            return {
                "error": "Client not found",
                "client_id": client_id
            }
    
    # Enhance with percentile information
    total_clients = len(all_entries.data)
    percentile = round((1 - (client_entry["rank"] / total_clients)) * 100, 1)
    client_entry["percentile"] = percentile
    client_entry["total_clients"] = total_clients
    client_entry["ranked"] = True
    
    return client_entry
