"""
Internal KPI Report Module

This module provides functionality for generating internal KPI reports for administrators
and management, focusing on badge system performance metrics.
"""

import uuid
import logging
from datetime import datetime, timedelta
from .pdf_generator import generate_pdf
from core.supabase.client import supabase_admin

# Configure logger
logger = logging.getLogger(__name__)


async def create_kpi_report(timeframe="month", compare_previous=True):
    """
    Create a comprehensive KPI report for internal use, focusing on badge system
    performance and engagement metrics.
    
    Args:
        timeframe (str): The time period to analyze (week, month, quarter, year)
        compare_previous (bool): Whether to include comparison with the previous time period
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Get current time period stats
        current_stats_response = supabase_admin \
            .rpc(
                "get_global_badge_statistics",
                {"timeframe_param": timeframe}
            ) \
            .execute()
        
        current_stats = current_stats_response.data[0] if current_stats_response.data else {}
        
        # Get previous time period stats if requested
        previous_stats = {}
        if compare_previous:
            previous_stats_response = supabase_admin \
                .rpc(
                    "get_global_badge_statistics_previous_period",
                    {"timeframe_param": timeframe}
                ) \
                .execute()
            
            previous_stats = previous_stats_response.data[0] if previous_stats_response.data else {}
        
        # Get region breakdown
        region_breakdown_response = supabase_admin \
            .rpc(
                "get_region_badge_breakdown",
                {"timeframe_param": timeframe}
            ) \
            .execute()
        
        region_breakdown = region_breakdown_response.data or []
        
        # Get achievement statistics
        achievement_stats_response = supabase_admin \
            .rpc(
                "get_achievement_statistics",
                {"timeframe_param": timeframe}
            ) \
            .execute()
        
        achievement_stats = achievement_stats_response.data or []
        
        # Get top and bottom performing clients
        top_clients_response = supabase_admin \
            .rpc(
                "get_badge_leaderboard",
                {"timeframe": timeframe, "limit_count": 10}
            ) \
            .execute()
        
        top_clients = top_clients_response.data
        
        bottom_clients_response = supabase_admin \
            .rpc(
                "get_badge_leaderboard_bottom",
                {"timeframe": timeframe, "limit_count": 10}
            ) \
            .execute()
        
        bottom_clients = bottom_clients_response.data
        
        # Calculate change percentages for KPIs if comparing to previous period
        changes = {}
        if compare_previous and previous_stats:
            for key in current_stats:
                if key in previous_stats and previous_stats[key] != 0:
                    change_pct = ((current_stats[key] - previous_stats[key]) / previous_stats[key]) * 100
                    changes[key] = round(change_pct, 1)
                else:
                    changes[key] = None  # No previous data to compare
        
        # Determine time period labels
        time_labels = get_time_period_labels(timeframe)
        
        # Prepare context for the template
        context = {
            "timeframe": timeframe,
            "timeframe_label": time_labels["current"],
            "previous_timeframe_label": time_labels["previous"] if compare_previous else None,
            "current_stats": current_stats,
            "previous_stats": previous_stats if compare_previous else None,
            "changes": changes,
            "region_breakdown": region_breakdown,
            "achievement_stats": achievement_stats,
            "top_clients": top_clients,
            "bottom_clients": bottom_clients,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": str(uuid.uuid4())[:8]
        }
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"internal_kpi_{timeframe}_{timestamp}.pdf"
        
        # Generate the PDF
        output_path = generate_pdf(
            "kpi_report_template.html", 
            context, 
            output_filename,
            css_files=["static/css/report_styles.css"]
        )
        
        logger.info(f"Generated internal KPI report: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating internal KPI report: {str(e)}")
        raise


async def create_executive_summary_report():
    """
    Create an executive summary report for senior management.
    
    This report provides a high-level overview of badge system performance
    across all regions and timeframes.
    
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Get overall badge system stats
        overall_stats_response = supabase_admin \
            .rpc(
                "get_global_badge_statistics",
                {"timeframe_param": "all"}
            ) \
            .execute()
        
        overall_stats = overall_stats_response.data[0] if overall_stats_response.data else {}
        
        # Get stats for different time periods
        time_periods = ["week", "month", "quarter", "year"]
        period_stats = {}
        
        for period in time_periods:
            period_response = supabase_admin \
                .rpc(
                    "get_global_badge_statistics",
                    {"timeframe_param": period}
                ) \
                .execute()
            
            period_stats[period] = period_response.data[0] if period_response.data else {}
        
        # Get top regions
        top_regions_response = supabase_admin \
            .rpc(
                "get_top_badge_regions",
                {"limit_count": 5}
            ) \
            .execute()
        
        top_regions = top_regions_response.data
        
        # Get monthly trends
        monthly_trends_response = supabase_admin \
            .rpc(
                "get_monthly_badge_trends",
                {"months_count": 12}
            ) \
            .execute()
        
        monthly_trends = monthly_trends_response.data or []
        
        # Get achievement distribution
        achievement_distribution_response = supabase_admin \
            .rpc(
                "get_achievement_type_distribution"
            ) \
            .execute()
        
        achievement_distribution = achievement_distribution_response.data or []
        
        # Prepare context for the template
        context = {
            "overall_stats": overall_stats,
            "period_stats": period_stats,
            "top_regions": top_regions,
            "monthly_trends": monthly_trends,
            "achievement_distribution": achievement_distribution,
            "current_month": datetime.now().strftime("%B %Y"),
            "last_30_days_stats": period_stats.get("month", {}),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": str(uuid.uuid4())[:8]
        }
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"executive_summary_{timestamp}.pdf"
        
        # Generate the PDF
        output_path = generate_pdf(
            "executive_summary_template.html", 
            context, 
            output_filename,
            css_files=["static/css/report_styles.css"]
        )
        
        logger.info(f"Generated executive summary report: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating executive summary report: {str(e)}")
        raise


def get_time_period_labels(timeframe):
    """
    Get human-readable labels for current and previous time periods.
    
    Args:
        timeframe (str): The time period type (week, month, quarter, year)
        
    Returns:
        dict: Dictionary with 'current' and 'previous' time period labels
    """
    now = datetime.now()
    
    if timeframe == "week":
        # Current week is "Week X of YYYY" (e.g., Week 15 of 2025)
        week_number = now.isocalendar()[1]
        year = now.year
        current = f"Week {week_number} of {year}"
        
        # Previous week
        prev_week = now - timedelta(weeks=1)
        prev_week_number = prev_week.isocalendar()[1]
        prev_year = prev_week.year
        previous = f"Week {prev_week_number} of {prev_year}"
    
    elif timeframe == "month":
        # Current month is "Month YYYY" (e.g., April 2025)
        current = now.strftime("%B %Y")
        
        # Previous month
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
        
        prev_date = datetime(prev_year, prev_month, 1)
        previous = prev_date.strftime("%B %Y")
    
    elif timeframe == "quarter":
        # Current quarter is "QX YYYY" (e.g., Q2 2025)
        quarter = (now.month - 1) // 3 + 1
        current = f"Q{quarter} {now.year}"
        
        # Previous quarter
        if quarter == 1:
            prev_quarter = 4
            prev_year = now.year - 1
        else:
            prev_quarter = quarter - 1
            prev_year = now.year
        
        previous = f"Q{prev_quarter} {prev_year}"
    
    elif timeframe == "year":
        # Current year is "YYYY" (e.g., 2025)
        current = str(now.year)
        
        # Previous year
        previous = str(now.year - 1)
    
    else:  # All time or unknown
        current = "All Time"
        previous = "N/A"
    
    return {
        "current": current,
        "previous": previous
    }


async def get_internal_reports():
    """
    List all internal reports.
    
    Returns:
        list: List of report info dictionaries with filename and create date
    """
    from .pdf_generator import list_reports
    import os
    
    try:
        # Get all report files
        all_report_files = list_reports()
        
        # Filter for internal reports
        report_files = [f for f in all_report_files if f.startswith("internal_kpi_") or f.startswith("executive_summary_")]
        
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
        logger.error(f"Error listing internal reports: {str(e)}")
        return []
