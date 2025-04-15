"""
Client Report Module

This module provides functionality for generating client-specific badge and achievement reports.
"""

import uuid
import logging
from datetime import datetime
from .pdf_generator import generate_pdf
from core.supabase.client import supabase_admin

# Configure logger
logger = logging.getLogger(__name__)


async def create_client_report(client_id, include_achievements=True):
    """
    Create a comprehensive PDF report for a client that includes their badge history
    and achievement records.
    
    Args:
        client_id (str): The unique identifier for the client
        include_achievements (bool): Whether to include achievements in the report
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Fetch client data
        client_response = supabase_admin \
            .from_("clients") \
            .select("name, email, region") \
            .eq("id", client_id) \
            .single() \
            .execute()
        
        if not client_response.data:
            logger.error(f"Client not found: {client_id}")
            raise ValueError(f"Client not found: {client_id}")
        
        client_info = client_response.data
        
        # Fetch badge history for the client
        badge_response = supabase_admin \
            .from_("badge_history") \
            .select("*") \
            .eq("client_id", client_id) \
            .order("week_id", desc=True) \
            .execute()
        
        badge_data = badge_response.data
        
        # Prepare badge statistics
        total_badges = sum(1 for badge in badge_data if badge.get('earned', False))
        total_weeks = len(badge_data)
        compliance_rate = (total_badges / total_weeks * 100) if total_weeks > 0 else 0
        
        # Get current streak
        streak_response = supabase_admin \
            .rpc("get_streak_count", {"client_id": client_id}) \
            .execute()
        
        current_streak = streak_response.data or 0
        
        # Fetch achievements if requested
        achievements = []
        if include_achievements:
            achievements_response = supabase_admin \
                .from_("achievement_log") \
                .select("*") \
                .eq("client_id", client_id) \
                .order("earned_at", desc=True) \
                .execute()
            
            achievements = achievements_response.data
        
        # Prepare context for the template
        context = {
            "client_name": client_info.get("name", ""),
            "client_email": client_info.get("email", ""),
            "client_region": client_info.get("region", ""),
            "badge_data": badge_data,
            "achievements": achievements,
            "total_badges": total_badges,
            "total_weeks": total_weeks,
            "compliance_rate": round(compliance_rate, 1),
            "current_streak": current_streak,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": str(uuid.uuid4())[:8]
        }
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{client_id}_badge_report_{timestamp}.pdf"
        
        # Generate the PDF
        output_path = generate_pdf(
            "client_report_template.html", 
            context, 
            output_filename,
            css_files=["static/css/report_styles.css"]
        )
        
        logger.info(f"Generated client report: {output_path} for client: {client_id}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating client report: {str(e)}")
        raise


async def create_client_summary_report(client_ids=None, region=None):
    """
    Create a summary report for multiple clients, either specified by IDs or by region.
    
    Args:
        client_ids (list): Optional list of client IDs to include in the report
        region (str): Optional region to filter clients by
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Query to get clients
        query = supabase_admin.from_("clients").select("id, name, email, region")
        
        # Apply filters
        if client_ids:
            query = query.in_("id", client_ids)
        
        if region:
            query = query.eq("region", region)
        
        clients_response = query.execute()
        clients = clients_response.data
        
        if not clients:
            logger.error("No clients found matching the criteria")
            raise ValueError("No clients found matching the criteria")
        
        # Collect badge and achievement data for each client
        client_summaries = []
        
        for client in clients:
            # Get badge statistics
            badge_response = supabase_admin \
                .rpc(
                    "get_client_badge_summary", 
                    {"client_id_param": client["id"]}
                ) \
                .execute()
            
            badge_summary = badge_response.data[0] if badge_response.data else {}
            
            # Get achievement count
            achievement_count_response = supabase_admin \
                .from_("achievement_log") \
                .select("id", count="exact") \
                .eq("client_id", client["id"]) \
                .execute()
            
            achievement_count = achievement_count_response.count
            
            # Combine client info with stats
            client_summaries.append({
                "id": client["id"],
                "name": client["name"],
                "email": client["email"],
                "region": client["region"],
                "badges_earned": badge_summary.get("badges_earned", 0),
                "compliance_rate": badge_summary.get("compliance_rate", 0),
                "streak": badge_summary.get("current_streak", 0),
                "achievement_count": achievement_count
            })
        
        # Sort by badge count (descending)
        client_summaries.sort(key=lambda x: (x["badges_earned"], x["compliance_rate"]), reverse=True)
        
        # Prepare context for the template
        context = {
            "clients": client_summaries,
            "region": region or "All Regions",
            "total_clients": len(clients),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": str(uuid.uuid4())[:8]
        }
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"client_summary_report_{timestamp}.pdf"
        if region:
            output_filename = f"{region}_summary_report_{timestamp}.pdf"
        
        # Generate the PDF
        output_path = generate_pdf(
            "client_summary_template.html", 
            context, 
            output_filename,
            css_files=["static/css/report_styles.css"]
        )
        
        logger.info(f"Generated client summary report: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating client summary report: {str(e)}")
        raise


async def get_client_reports(client_id=None):
    """
    List all reports for a client, or all client reports if no client ID is provided.
    
    Args:
        client_id (str, optional): The client ID to filter reports by
        
    Returns:
        list: List of report info dictionaries with filename and create date
    """
    from .pdf_generator import list_reports
    import os
    
    try:
        report_files = list_reports(client_id)
        
        # Extract additional info for each report
        reports = []
        for filename in report_files:
            file_path = os.path.join("exports", filename)
            create_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            reports.append({
                "filename": filename,
                "created_at": create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"/exports/{filename}",
                "size_kb": round(os.path.getsize(file_path) / 1024, 1)
            })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        return reports
    
    except Exception as e:
        logger.error(f"Error listing client reports: {str(e)}")
        return []
