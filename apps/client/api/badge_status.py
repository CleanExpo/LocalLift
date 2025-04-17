"""
Badge Status API

This module provides endpoints for retrieving client badge status
based on their posting activity for the current week.
"""

from fastapi import APIRouter
from core.supabase import supabase_admin_client
from datetime import datetime
from collections import Counter

router = APIRouter()

@router.get("/api/client/{client_id}/badge-status")
async def get_badge_status(client_id: str):
    """
    Get the badge status for a client based on their posting activity in the current week.
    
    Args:
        client_id: The unique identifier for the client
        
    Returns:
        A dictionary containing badge status, message, and post statistics
    """
    # Get current ISO week
    current_week = datetime.now().isocalendar()
    week_id = f"{current_week[0]}-W{str(current_week[1]).zfill(2)}"

    # Pull this week's posts using admin client for elevated permissions
    response = supabase_admin_client \
        .from_("gmb_posts") \
        .select("*") \
        .eq("client_id", client_id) \
        .eq("week_id", week_id) \
        .execute()

    posts = response.data or []
    total = len(posts)
    compliant = sum(1 for p in posts if p.get("compliant") is True)

    # Badge logic
    badge_earned = total >= 5 and compliant == 5
    
    # Save result to badge history if not already recorded
    existing = supabase_admin_client \
        .from_("badge_history") \
        .select("id") \
        .eq("client_id", client_id) \
        .eq("week_id", week_id) \
        .maybe_single() \
        .execute()

    if not existing.data:
        supabase_admin_client \
            .from_("badge_history") \
            .insert({
                "client_id": client_id,
                "week_id": week_id,
                "earned": badge_earned,
                "compliant": compliant,
                "total": total
            }) \
            .execute()
    
    if badge_earned:
        return {
            "badge": True,
            "message": "🎖️ Congrats! You earned your weekly compliance badge!",
            "compliant": compliant,
            "total": total
        }
    else:
        return {
            "badge": False,
            "message": f"You posted {compliant}/{total} times this week. Keep pushing to get your badge!",
            "compliant": compliant,
            "total": total
        }
