"""
Recognition Engine Module

This module provides tools for identifying and rewarding champion users within the LocalLift platform.
It analyzes user activity, achievements, and influence to highlight successful users and provide public recognition.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timedelta

from core.auth.auth_utils import get_current_user, get_admin_user
from core.supabase.client import supabase_admin_client

# Configure logger
logger = logging.getLogger(__name__)

# Set up router
router = APIRouter(prefix="/champions", tags=["champions"])

# Configure templates
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def champions_dashboard(
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    Render the champions dashboard showing recognized champions across regions.
    """
    try:
        # Get all active regions
        regions_response = supabase_admin_client \
            .from_("regions") \
            .select("id, name, region_code, status") \
            .eq("status", "active") \
            .execute()
        
        regions = regions_response.data or []
        
        # Get champions for each region
        all_champions = []
        for region in regions:
            region_id = region["id"]
            
            # Get champions for this region
            champions_query = """
                SELECT c.id, c.name, c.business_name, c.email, c.region_id,
                    (SELECT COUNT(*) FROM badge_history WHERE client_id = c.id AND earned = true) as badges,
                    (SELECT MAX(streak_length) FROM client_streaks WHERE client_id = c.id) as max_streak,
                    (SELECT COUNT(*) FROM achievement_log WHERE client_id = c.id) as achievements,
                    (SELECT COUNT(*) FROM referral_tracker WHERE referrer_id = c.id AND status = 'converted') as referrals
                FROM clients c
                WHERE c.region_id = '{region_id}'
                AND c.active = true
                ORDER BY badges DESC, max_streak DESC, achievements DESC
                LIMIT 5
            """.format(region_id=region_id)
            
            champions_response = supabase_admin_client.rpc("run_query", {"query_text": champions_query}).execute()
            champions = champions_response.data or []
            
            if champions:
                # Add region info to champions
                for champion in champions:
                    champion["region_name"] = region["name"]
                    champion["region_code"] = region["region_code"]
                    
                    # Calculate champion score (weighted)
                    champion["score"] = (
                        (champion.get("badges", 0) * 10) +
                        (champion.get("max_streak", 0) * 5) +
                        (champion.get("achievements", 0) * 2) +
                        (champion.get("referrals", 0) * 15)
                    )
                
                all_champions.extend(champions)
        
        # Sort all champions by score
        all_champions.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Group champions by region
        champions_by_region = {}
        for champion in all_champions:
            region_id = champion["region_id"]
            if region_id not in champions_by_region:
                champions_by_region[region_id] = []
            
            champions_by_region[region_id].append(champion)
        
        # Get top champions overall
        top_champions = all_champions[:10] if len(all_champions) >= 10 else all_champions
        
        # Get featured champion (highest score)
        featured_champion = all_champions[0] if all_champions else None
        
        return templates.TemplateResponse(
            "champions/dashboard.html",
            {
                "request": request,
                "regions": regions,
                "champions_by_region": champions_by_region,
                "top_champions": top_champions,
                "featured_champion": featured_champion,
                "user": current_user
            }
        )
        
    except Exception as e:
        logger.error(f"Error displaying champions dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error displaying champions dashboard: {str(e)}"
        )


@router.get("/leaderboard", response_class=HTMLResponse)
async def champions_leaderboard(
    request: Request,
    region_id: Optional[str] = None,
    timeframe: Optional[str] = "all",
    current_user = Depends(get_current_user)
):
    """
    Show a leaderboard of champions filtered by region and timeframe.
    """
    try:
        # Get all regions for filter
        regions_response = supabase_admin_client \
            .from_("regions") \
            .select("id, name, region_code, status") \
            .order("name", asc=True) \
            .execute()
        
        regions = regions_response.data or []
        
        # Set up date filter based on timeframe
        date_filter = ""
        if timeframe == "week":
            date_filter = f"AND bh.created_at >= '{datetime.now() - timedelta(days=7)}'"
        elif timeframe == "month":
            date_filter = f"AND bh.created_at >= '{datetime.now() - timedelta(days=30)}'"
        elif timeframe == "quarter":
            date_filter = f"AND bh.created_at >= '{datetime.now() - timedelta(days=90)}'"
        
        # Set up region filter
        region_filter = ""
        selected_region = None
        if region_id:
            region_filter = f"AND c.region_id = '{region_id}'"
            
            # Get selected region info
            for region in regions:
                if region["id"] == region_id:
                    selected_region = region
                    break
        
        # Get leaderboard
        leaderboard_query = f"""
            SELECT 
                c.id, 
                c.name, 
                c.business_name, 
                c.region_id,
                r.name as region_name,
                COUNT(DISTINCT bh.id) as badges,
                MAX(cs.streak_length) as max_streak,
                COUNT(DISTINCT al.id) as achievements,
                COUNT(DISTINCT rt.id) as referrals
            FROM clients c
            JOIN regions r ON c.region_id = r.id
            LEFT JOIN badge_history bh ON c.id = bh.client_id AND bh.earned = true {date_filter}
            LEFT JOIN client_streaks cs ON c.id = cs.client_id
            LEFT JOIN achievement_log al ON c.id = al.client_id {date_filter}
            LEFT JOIN referral_tracker rt ON c.id = rt.referrer_id AND rt.status = 'converted' {date_filter}
            WHERE c.active = true
            {region_filter}
            GROUP BY c.id, c.name, c.business_name, c.region_id, r.name
            ORDER BY badges DESC, max_streak DESC, achievements DESC, referrals DESC
            LIMIT 100
        """
        
        leaderboard_response = supabase_admin_client.rpc("run_query", {"query_text": leaderboard_query}).execute()
        leaderboard = leaderboard_response.data or []
        
        # Calculate scores and ranks
        for i, entry in enumerate(leaderboard):
            # Calculate champion score (weighted)
            entry["score"] = (
                (entry.get("badges", 0) * 10) +
                (entry.get("max_streak", 0) * 5) +
                (entry.get("achievements", 0) * 2) +
                (entry.get("referrals", 0) * 15)
            )
            
            # Assign rank
            entry["rank"] = i + 1
        
        return templates.TemplateResponse(
            "champions/leaderboard.html",
            {
                "request": request,
                "regions": regions,
                "leaderboard": leaderboard,
                "selected_region": selected_region,
                "timeframe": timeframe,
                "user": current_user
            }
        )
        
    except Exception as e:
        logger.error(f"Error displaying champions leaderboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error displaying champions leaderboard: {str(e)}"
        )


@router.get("/profile/{client_id}", response_class=HTMLResponse)
async def champion_profile(
    request: Request,
    client_id: str,
    current_user = Depends(get_current_user)
):
    """
    Show a detailed profile for a champion.
    """
    try:
        # Get client data
        client_response = supabase_admin_client \
            .from_("clients") \
            .select("*, regions(name, region_code)") \
            .eq("id", client_id) \
            .single() \
            .execute()
        
        if not client_response.data:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )
        
        client = client_response.data
        
        # Get badge data
        badge_response = supabase_admin_client \
            .from_("badge_history") \
            .select("*") \
            .eq("client_id", client_id) \
            .eq("earned", True) \
            .order("created_at", desc=True) \
            .execute()
        
        badges = badge_response.data or []
        
        # Get streak data
        streak_response = supabase_admin_client \
            .from_("client_streaks") \
            .select("*") \
            .eq("client_id", client_id) \
            .order("streak_length", desc=True) \
            .limit(1) \
            .execute()
        
        streak = streak_response.data[0] if streak_response.data else {"streak_length": 0}
        
        # Get achievements
        achievements_response = supabase_admin_client \
            .from_("achievement_log") \
            .select("*") \
            .eq("client_id", client_id) \
            .order("created_at", desc=True) \
            .execute()
        
        achievements = achievements_response.data or []
        
        # Get referrals
        referrals_response = supabase_admin_client \
            .from_("referral_tracker") \
            .select("*, clients(name, business_name)") \
            .eq("referrer_id", client_id) \
            .eq("status", "converted") \
            .execute()
        
        referrals = referrals_response.data or []
        
        # Calculate champion score
        score = (
            (len(badges) * 10) +
            (streak["streak_length"] * 5) +
            (len(achievements) * 2) +
            (len(referrals) * 15)
        )
        
        # Get champion rank
        rank_query = f"""
            WITH champion_scores AS (
                SELECT 
                    c.id,
                    (COUNT(DISTINCT bh.id) * 10) + 
                    (MAX(COALESCE(cs.streak_length, 0)) * 5) + 
                    (COUNT(DISTINCT al.id) * 2) + 
                    (COUNT(DISTINCT rt.id) * 15) as score
                FROM clients c
                LEFT JOIN badge_history bh ON c.id = bh.client_id AND bh.earned = true
                LEFT JOIN client_streaks cs ON c.id = cs.client_id
                LEFT JOIN achievement_log al ON c.id = al.client_id
                LEFT JOIN referral_tracker rt ON c.id = rt.referrer_id AND rt.status = 'converted'
                WHERE c.active = true
                GROUP BY c.id
            )
            SELECT 
                COUNT(*) + 1
            FROM champion_scores
            WHERE score > (
                SELECT score FROM champion_scores WHERE id = '{client_id}'
            )
        """
        
        rank_response = supabase_admin_client.rpc("run_query", {"query_text": rank_query}).execute()
        rank = rank_response.data[0]["count"] if rank_response.data else 1
        
        return templates.TemplateResponse(
            "champions/profile.html",
            {
                "request": request,
                "client": client,
                "badges": badges,
                "streak": streak,
                "achievements": achievements,
                "referrals": referrals,
                "score": score,
                "rank": rank,
                "user": current_user
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error displaying champion profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error displaying champion profile: {str(e)}"
        )


@router.get("/admin", response_class=HTMLResponse)
async def champions_admin(
    request: Request,
    current_user = Depends(get_admin_user)
):
    """
    Admin dashboard for managing champion recognition.
    """
    try:
        # Get configured recognition thresholds
        thresholds_response = supabase_admin_client \
            .from_("recognition_thresholds") \
            .select("*") \
            .execute()
        
        thresholds = thresholds_response.data or []
        
        # Group thresholds by type
        thresholds_by_type = {}
        for threshold in thresholds:
            threshold_type = threshold.get("type", "general")
            if threshold_type not in thresholds_by_type:
                thresholds_by_type[threshold_type] = []
            
            thresholds_by_type[threshold_type].append(threshold)
        
        # Get recognition events
        events_response = supabase_admin_client \
            .from_("recognition_events") \
            .select("*, clients(name, business_name, region_id, regions(name))") \
            .order("created_at", desc=True) \
            .limit(100) \
            .execute()
        
        events = events_response.data or []
        
        return templates.TemplateResponse(
            "admin/champions_admin.html",
            {
                "request": request,
                "thresholds_by_type": thresholds_by_type,
                "events": events,
                "user": current_user
            }
        )
        
    except Exception as e:
        logger.error(f"Error displaying champions admin: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error displaying champions admin: {str(e)}"
        )


@router.post("/admin/thresholds")
async def update_recognition_thresholds(
    request: Request,
    data: Dict[str, Any] = Form(...),
    current_user = Depends(get_admin_user)
):
    """
    Update recognition thresholds for champions.
    """
    try:
        # Process form data
        for key, value in data.items():
            if not key.startswith("threshold_"):
                continue
            
            # Extract threshold ID
            threshold_id = key.replace("threshold_", "")
            
            # Update threshold
            update_response = supabase_admin_client \
                .from_("recognition_thresholds") \
                .update({"value": value}) \
                .eq("id", threshold_id) \
                .execute()
            
            if not update_response.data:
                logger.warning(f"Failed to update threshold {threshold_id}")
        
        # Redirect to admin dashboard
        return HTMLResponse(
            f"""
            <html>
                <head>
                    <meta http-equiv="refresh" content="3;url=/champions/admin" />
                </head>
                <body>
                    <h1>Thresholds Updated Successfully</h1>
                    <p>Redirecting to admin dashboard...</p>
                </body>
            </html>
            """
        )
        
    except Exception as e:
        logger.error(f"Error updating recognition thresholds: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating recognition thresholds: {str(e)}"
        )


@router.post("/admin/recognize")
async def manually_recognize_champion(
    client_id: str = Form(...),
    achievement_type: str = Form(...),
    notes: Optional[str] = Form(None),
    tasks: BackgroundTasks = None,
    current_user = Depends(get_admin_user)
):
    """
    Manually recognize a client as a champion.
    """
    try:
        # Get client data
        client_response = supabase_admin_client \
            .from_("clients") \
            .select("*") \
            .eq("id", client_id) \
            .single() \
            .execute()
        
        if not client_response.data:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )
        
        client = client_response.data
        
        # Create recognition event
        event_data = {
            "client_id": client_id,
            "type": achievement_type,
            "notes": notes,
            "created_by": current_user["id"],
            "automatic": False
        }
        
        event_response = supabase_admin_client \
            .from_("recognition_events") \
            .insert(event_data) \
            .execute()
        
        if not event_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create recognition event"
            )
        
        # Create achievement in achievement log
        achievement_data = {
            "client_id": client_id,
            "type": "champion_recognition",
            "label": f"Champion Recognition - {achievement_type}",
            "description": notes or f"Recognized as a champion for {achievement_type}",
            "points": 100  # Arbitrary point value
        }
        
        supabase_admin_client \
            .from_("achievement_log") \
            .insert(achievement_data) \
            .execute()
        
        # Schedule notification
        if tasks:
            tasks.add_task(
                notify_champion_recognition,
                client_id=client_id,
                achievement_type=achievement_type
            )
        
        return JSONResponse({
            "success": True,
            "message": f"Client {client['name']} successfully recognized as a champion for {achievement_type}"
        })
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error recognizing champion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error recognizing champion: {str(e)}"
        )


@router.post("/scan")
async def scan_for_champions(
    tasks: BackgroundTasks = None,
    current_user = Depends(get_admin_user)
):
    """
    Scan for clients that meet champion criteria.
    """
    try:
        # Schedule background task
        if tasks:
            tasks.add_task(scan_for_champion_candidates)
        
        return JSONResponse({
            "success": True,
            "message": "Champion scanning process started in background"
        })
        
    except Exception as e:
        logger.error(f"Error starting champion scan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting champion scan: {str(e)}"
        )


# Background tasks

async def notify_champion_recognition(client_id: str, achievement_type: str):
    """
    Send notifications for champion recognition.
    """
    try:
        # Get client data
        client_response = supabase_admin_client \
            .from_("clients") \
            .select("*") \
            .eq("id", client_id) \
            .single() \
            .execute()
        
        if not client_response.data:
            logger.error(f"Client not found for notification: {client_id}")
            return
        
        client = client_response.data
        
        # In a real implementation, this would send an email notification
        logger.info(f"Champion recognition notification would be sent to {client['name']} ({client['email']})")
        
        # Log the notification
        supabase_admin_client \
            .from_("client_notifications") \
            .insert({
                "client_id": client_id,
                "type": "champion_recognition",
                "content": f"Congratulations! You've been recognized as a champion for {achievement_type}.",
                "sent_at": "now()"
            }) \
            .execute()
        
    except Exception as e:
        logger.error(f"Error sending champion recognition notification: {str(e)}")


async def scan_for_champion_candidates():
    """
    Scan for clients that meet champion criteria.
    This is a background task that runs periodically.
    """
    try:
        # Get recognition thresholds
        thresholds_response = supabase_admin_client \
            .from_("recognition_thresholds") \
            .select("*") \
            .execute()
        
        thresholds = thresholds_response.data or []
        
        # Convert thresholds to dictionary
        threshold_values = {}
        for threshold in thresholds:
            threshold_values[threshold.get("type", "general")] = int(threshold.get("value", 0))
        
        # Default thresholds if not configured
        badge_threshold = threshold_values.get("badges", 10)
        streak_threshold = threshold_values.get("streak", 8)
        referral_threshold = threshold_values.get("referrals", 3)
        
        # Find clients that meet champion criteria
        champion_query = f"""
            SELECT 
                c.id, 
                c.name, 
                c.business_name, 
                c.email,
                COUNT(DISTINCT bh.id) as badges,
                MAX(cs.streak_length) as max_streak,
                COUNT(DISTINCT rt.id) as referrals
            FROM clients c
            LEFT JOIN badge_history bh ON c.id = bh.client_id AND bh.earned = true
            LEFT JOIN client_streaks cs ON c.id = cs.client_id
            LEFT JOIN referral_tracker rt ON c.id = rt.referrer_id AND rt.status = 'converted'
            WHERE c.active = true
            GROUP BY c.id, c.name, c.business_name, c.email
            HAVING 
                COUNT(DISTINCT bh.id) >= {badge_threshold} OR
                MAX(cs.streak_length) >= {streak_threshold} OR
                COUNT(DISTINCT rt.id) >= {referral_threshold}
        """
        
        champions_response = supabase_admin_client.rpc("run_query", {"query_text": champion_query}).execute()
        candidates = champions_response.data or []
        
        # Get existing recognitions
        recognitions_response = supabase_admin_client \
            .from_("recognition_events") \
            .select("client_id, type") \
            .execute()
        
        recognitions = recognitions_response.data or []
        
        # Map of client_id to list of recognition types
        client_recognitions = {}
        for rec in recognitions:
            client_id = rec["client_id"]
            if client_id not in client_recognitions:
                client_recognitions[client_id] = []
            
            client_recognitions[client_id].append(rec["type"])
        
        # Process each candidate
        for candidate in candidates:
            client_id = candidate["id"]
            badges = candidate.get("badges", 0)
            max_streak = candidate.get("max_streak", 0)
            referrals = candidate.get("referrals", 0)
            
            # Skip if already recognized for a type
            existing_recognitions = client_recognitions.get(client_id, [])
            
            # Check if meets badge champion threshold
            if badges >= badge_threshold and "badge_champion" not in existing_recognitions:
                # Create recognition event
                event_data = {
                    "client_id": client_id,
                    "type": "badge_champion",
                    "notes": f"Automatically recognized for earning {badges} badges",
                    "automatic": True
                }
                
                supabase_admin_client \
                    .from_("recognition_events") \
                    .insert(event_data) \
                    .execute()
                
                # Create achievement
                achievement_data = {
                    "client_id": client_id,
                    "type": "champion_recognition",
                    "label": "Badge Champion",
                    "description": f"Recognized for earning {badges} badges",
                    "points": 100
                }
                
                supabase_admin_client \
                    .from_("achievement_log") \
                    .insert(achievement_data) \
                    .execute()
                
                # Send notification
                await notify_champion_recognition(client_id, "Badge Champion")
            
            # Check if meets streak champion threshold
            if max_streak >= streak_threshold and "streak_champion" not in existing_recognitions:
                # Create recognition event
                event_data = {
                    "client_id": client_id,
                    "type": "streak_champion",
                    "notes": f"Automatically recognized for maintaining a {max_streak}-week streak",
                    "automatic": True
                }
                
                supabase_admin_client \
                    .from_("recognition_events") \
                    .insert(event_data) \
                    .execute()
                
                # Create achievement
                achievement_data = {
                    "client_id": client_id,
                    "type": "champion_recognition",
                    "label": "Streak Champion",
                    "description": f"Recognized for maintaining a {max_streak}-week streak",
                    "points": 100
                }
                
                supabase_admin_client \
                    .from_("achievement_log") \
                    .insert(achievement_data) \
                    .execute()
                
                # Send notification
                await notify_champion_recognition(client_id, "Streak Champion")
            
            # Check if meets referral champion threshold
            if referrals >= referral_threshold and "referral_champion" not in existing_recognitions:
                # Create recognition event
                event_data = {
                    "client_id": client_id,
                    "type": "referral_champion",
                    "notes": f"Automatically recognized for {referrals} successful referrals",
                    "automatic": True
                }
                
                supabase_admin_client \
                    .from_("recognition_events") \
                    .insert(event_data) \
                    .execute()
                
                # Create achievement
                achievement_data = {
                    "client_id": client_id,
                    "type": "champion_recognition",
                    "label": "Referral Champion",
                    "description": f"Recognized for {referrals} successful referrals",
                    "points": 100
                }
                
                supabase_admin_client \
                    .from_("achievement_log") \
                    .insert(achievement_data) \
                    .execute()
                
                # Send notification
                await notify_champion_recognition(client_id, "Referral Champion")
        
        logger.info(f"Champion scan completed, processed {len(candidates)} candidates")
        
    except Exception as e:
        logger.error(f"Error scanning for champions: {str(e)}")
