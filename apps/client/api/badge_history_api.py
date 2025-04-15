"""
Badge History API

This module provides endpoints for retrieving and analyzing client badge history,
allowing clients to see their badge earning patterns over time.
"""

from fastapi import APIRouter, HTTPException, status
from core.supabase import supabase_admin_client
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import calendar

router = APIRouter()

@router.get("/api/client/{client_id}/badge-history")
async def get_badge_history(
    client_id: str, 
    limit: Optional[int] = 12
):
    """
    Get badge history for a client.
    
    Args:
        client_id: The unique identifier for the client
        limit: Number of weeks to return (default is 12 weeks)
        
    Returns:
        A list of badge history records, ordered by week_id descending
    """
    try:
        # Pull badge history from database
        response = supabase_admin_client \
            .from_("badge_history") \
            .select("*") \
            .eq("client_id", client_id) \
            .order("week_id", option="desc") \
            .limit(limit) \
            .execute()
        
        history = response.data or []
        
        # Convert ISO week format to more readable dates
        for record in history:
            year, week = record["week_id"].split("-W")
            year = int(year)
            week = int(week)
            
            # Find the first day of the ISO week
            # ISO week starts on Monday
            first_day = datetime.fromisocalendar(year, week, 1)
            last_day = first_day + timedelta(days=6)
            
            # Add formatted date ranges
            record["start_date"] = first_day.strftime("%b %d")
            record["end_date"] = last_day.strftime("%b %d")
            record["date_range"] = f"{record['start_date']} - {record['end_date']}"
        
        return history
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve badge history: {str(e)}"
        )


@router.get("/api/client/{client_id}/badge-statistics")
async def get_badge_statistics(client_id: str):
    """
    Get badge statistics for a client.
    
    Args:
        client_id: The unique identifier for the client
        
    Returns:
        Statistical information about the client's badge earning history
    """
    try:
        # Get all badge history for the client
        response = supabase_admin_client \
            .from_("badge_history") \
            .select("*") \
            .eq("client_id", client_id) \
            .execute()
        
        history = response.data or []
        
        if not history:
            return {
                "total_weeks": 0,
                "badges_earned": 0,
                "compliance_rate": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "total_compliant_posts": 0,
                "total_posts": 0,
                "average_weekly_posts": 0,
                "history_available": False
            }
        
        # Sort by week_id for streak calculation
        sorted_history = sorted(history, key=lambda x: x["week_id"])
        
        # Calculate statistics
        total_weeks = len(history)
        badges_earned = sum(1 for record in history if record["earned"])
        total_compliant_posts = sum(record["compliant"] for record in history)
        total_posts = sum(record["total"] for record in history)
        
        # Calculate streak
        current_streak = 0
        longest_streak = 0
        current_count = 0
        
        for record in reversed(sorted_history):
            if record["earned"]:
                current_count += 1
                longest_streak = max(longest_streak, current_count)
            else:
                if current_count > 0:
                    # Only update current_streak the first time we break
                    if current_streak == 0:
                        current_streak = current_count
                current_count = 0
        
        # If we ended on a streak, update current_streak
        if current_count > 0:
            current_streak = current_count
        
        longest_streak = max(longest_streak, current_count)
        
        return {
            "total_weeks": total_weeks,
            "badges_earned": badges_earned,
            "compliance_rate": round(badges_earned / total_weeks * 100 if total_weeks > 0 else 0, 1),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_compliant_posts": total_compliant_posts,
            "total_posts": total_posts,
            "average_weekly_posts": round(total_posts / total_weeks, 1) if total_weeks > 0 else 0,
            "history_available": True
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve badge statistics: {str(e)}"
        )


@router.get("/api/admin/badges/leaderboard")
async def get_badge_leaderboard(
    limit: Optional[int] = 10,
    timeframe: Optional[str] = "all"
):
    """
    Get the badge leaderboard for all clients.
    
    Args:
        limit: Number of clients to return
        timeframe: Time period for the leaderboard ('week', 'month', 'quarter', 'year', 'all')
        
    Returns:
        Leaderboard of clients ranked by badge earning performance
    """
    try:
        # Determine date range based on timeframe
        now = datetime.now()
        current_week = now.isocalendar()
        current_week_id = f"{current_week[0]}-W{str(current_week[1]).zfill(2)}"
        
        # Query for all clients' badge history
        query = supabase_admin_client.from_("badge_history").select("*")
        
        if timeframe == "week":
            query = query.eq("week_id", current_week_id)
        elif timeframe == "month":
            # Get current month's badge history
            start_of_month = datetime(now.year, now.month, 1)
            # Calculate first week of month
            start_week = start_of_month.isocalendar()
            start_week_id = f"{start_week[0]}-W{str(start_week[1]).zfill(2)}"
            query = query.gte("week_id", start_week_id)
        elif timeframe == "quarter":
            # Calculate start of current quarter
            quarter_month = (now.month - 1) // 3 * 3 + 1
            start_of_quarter = datetime(now.year, quarter_month, 1)
            # Calculate first week of quarter
            start_week = start_of_quarter.isocalendar()
            start_week_id = f"{start_week[0]}-W{str(start_week[1]).zfill(2)}"
            query = query.gte("week_id", start_week_id)
        elif timeframe == "year":
            # Get current year's badge history
            query = query.like("week_id", f"{now.year}-%")
        
        # Execute query
        response = query.execute()
        history = response.data or []
        
        # Get client names for the leaderboard
        client_ids = list(set([record["client_id"] for record in history]))
        
        if not client_ids:
            return []
        
        clients_response = supabase_admin_client \
            .from_("clients") \
            .select("id, name, region") \
            .in_("id", client_ids) \
            .execute()
        
        clients = {client["id"]: client for client in clients_response.data or []}
        
        # Calculate badge stats per client
        client_stats = {}
        for record in history:
            client_id = record["client_id"]
            if client_id not in client_stats:
                client_stats[client_id] = {
                    "client_id": client_id,
                    "name": clients.get(client_id, {}).get("name", "Unknown"),
                    "region": clients.get(client_id, {}).get("region", "Unknown"),
                    "total_weeks": 0,
                    "badges_earned": 0,
                    "total_compliant_posts": 0,
                    "total_posts": 0
                }
            
            stats = client_stats[client_id]
            stats["total_weeks"] += 1
            stats["badges_earned"] += 1 if record["earned"] else 0
            stats["total_compliant_posts"] += record["compliant"]
            stats["total_posts"] += record["total"]
        
        # Calculate additional stats and sort
        leaderboard = []
        for client_id, stats in client_stats.items():
            stats["compliance_rate"] = round(stats["badges_earned"] / stats["total_weeks"] * 100, 1) if stats["total_weeks"] > 0 else 0
            stats["average_posts"] = round(stats["total_posts"] / stats["total_weeks"], 1) if stats["total_weeks"] > 0 else 0
            
            # Add to leaderboard
            leaderboard.append(stats)
        
        # Sort by badges earned (primary) and compliance rate (secondary)
        leaderboard.sort(key=lambda x: (x["badges_earned"], x["compliance_rate"]), reverse=True)
        
        # Apply limit
        return leaderboard[:limit]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve badge leaderboard: {str(e)}"
        )
