"""
Achievement API

This module provides API endpoints for client achievements,
allowing clients to view their earned achievements.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from core.supabase.client import supabase_admin
from core.auth.auth_utils import get_current_user

router = APIRouter()

@router.get("/api/client/{client_id}/achievements")
async def get_client_achievements(
    client_id: str,
    current_user = Depends(get_current_user)
):
    """
    Retrieve a client's achievements.
    
    Args:
        client_id: The client's unique identifier
        current_user: The authenticated user (from auth dependency)
        
    Returns:
        List of achievements earned by the client
    """
    # Check if user has permission to access these achievements
    if current_user["id"] != client_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access these achievements"
        )
    
    try:
        # Query achievements for the client, ordered by most recent first
        response = supabase_admin \
            .from_("achievement_log") \
            .select("*") \
            .eq("client_id", client_id) \
            .order("earned_at", desc=True) \
            .execute()
        
        return response.data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve achievements: {str(e)}"
        )


@router.post("/api/client/{client_id}/check-achievements")
async def check_client_achievements(
    client_id: str,
    current_user = Depends(get_current_user)
):
    """
    Manually check and update achievements for a client.
    
    This endpoint is useful for checking achievements after data migrations
    or for testing purposes.
    
    Args:
        client_id: The client's unique identifier
        current_user: The authenticated user (from auth dependency)
        
    Returns:
        Any newly earned achievements
    """
    # Check if user has permission to manage these achievements
    if current_user["id"] != client_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage these achievements"
        )
    
    try:
        # Call the check_achievements function in the database
        response = supabase_admin \
            .rpc("check_achievements", {"client_id": client_id}) \
            .execute()
        
        # Return the new achievements, or an empty list if none
        return response.data or []
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check achievements: {str(e)}"
        )


@router.get("/api/achievement-types")
async def get_achievement_types():
    """
    Get a list of all available achievement types and their criteria.
    
    This endpoint provides information about the different types of 
    achievements clients can earn in the system.
    
    Returns:
        List of achievement types and their criteria
    """
    # Return static information about achievement types
    return [
        {
            "type": "milestone",
            "criteria": [
                {"badges": 5, "label": "Bronze Badge Earned", "description": "Earn 5 weekly badges"},
                {"badges": 10, "label": "Silver Badge Earned", "description": "Earn 10 weekly badges"},
                {"badges": 20, "label": "Gold Badge Earned", "description": "Earn 20 weekly badges"}
            ]
        },
        {
            "type": "streak",
            "criteria": [
                {"weeks": 3, "label": "3-Week Streak Unlocked!", "description": "Earn badges for 3 consecutive weeks"},
                {"weeks": 5, "label": "5-Week Streak Unlocked!", "description": "Earn badges for 5 consecutive weeks"},
                {"weeks": 10, "label": "10-Week Streak Unlocked!", "description": "Earn badges for 10 consecutive weeks"}
            ]
        }
    ]
