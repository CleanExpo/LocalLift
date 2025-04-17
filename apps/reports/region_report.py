"""
Region Report Module

This module provides functionality for generating region-level badge and achievement reports.
"""

import uuid
import logging
from datetime import datetime
from .pdf_generator import generate_pdf
from core.supabase.client import supabase_admin

# Configure logger
logger = logging.getLogger(__name__)


async def create_region_report(region, timeframe="all"):
    """
    Create a comprehensive PDF report for a region that includes badge statistics
    and performance metrics.
    
    Args:
        region (str): The region name to generate a report for
        timeframe (str): The time period to analyze (week, month, quarter, year, all)
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Validate region
        regions_response = supabase_admin \
            .from_("clients") \
            .select("region", count="exact") \
            .eq("region", region) \
            .execute()
        
        if regions_response.count == 0:
            logger.error(f"Region not found: {region}")
            raise ValueError(f"Region not found: {region}")
        
        # Get clients in the region
        clients_response = supabase_admin \
            .from_("clients") \
            .select("id, name, email") \
            .eq("region", region) \
            .execute()
        
        clients = clients_response.data
        
        # Get badge statistics for the region
        region_stats_response = supabase_admin \
            .rpc(
                "get_region_badge_statistics",
                {"region_name": region, "timeframe_param": timeframe}
            ) \
            .execute()
        
        region_stats = region_stats_response.data[0] if region_stats_response.data else {}
        
        # Get top performing clients
        top_clients_response = supabase_admin \
            .rpc(
                "get_badge_leaderboard",
                {"region_filter": region, "timeframe": timeframe, "limit_count": 10}
            ) \
            .execute()
        
        top_clients = top_clients_response.data
        
        # Get achievements distribution
        achievements_response = supabase_admin \
            .rpc(
                "get_region_achievements_distribution",
                {"region_name": region}
            ) \
            .execute()
        
        achievements_distribution = achievements_response.data or []
        
        # Get historical data for trends (weekly badge earning rate)
        trends_response = supabase_admin \
            .rpc(
                "get_region_weekly_trends",
                {"region_name": region, "weeks_count": 12}
            ) \
            .execute()
        
        weekly_trends = trends_response.data or []
        
        # Calculate general stats
        total_clients = len(clients)
        active_clients = region_stats.get("active_clients", 0)
        total_badges = region_stats.get("total_badges", 0)
        participation_rate = region_stats.get("participation_rate", 0)
        compliance_rate = region_stats.get("compliance_rate", 0)
        
        # Prepare context for the template
        context = {
            "region_name": region,
            "timeframe": timeframe,
            "total_clients": total_clients,
            "active_clients": active_clients,
            "total_badges": total_badges,
            "participation_rate": round(participation_rate, 1),
            "compliance_rate": round(compliance_rate, 1),
            "top_clients": top_clients,
            "achievements_distribution": achievements_distribution,
            "weekly_trends": weekly_trends,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": str(uuid.uuid4())[:8]
        }
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"region_{region}_{timeframe}_{timestamp}.pdf"
        
        # Generate the PDF
        output_path = generate_pdf(
            "region_report_template.html", 
            context, 
            output_filename,
            css_files=["static/css/report_styles.css"]
        )
        
        logger.info(f"Generated region report: {output_path} for region: {region}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating region report: {str(e)}")
        raise


async def create_regions_comparison_report(regions=None, timeframe="all"):
    """
    Create a report comparing performance across multiple regions.
    
    Args:
        regions (list): List of regions to include in the comparison. If None, all regions are included.
        timeframe (str): The time period to analyze (week, month, quarter, year, all)
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Get all regions if not specified
        if not regions:
            regions_response = supabase_admin \
                .from_("clients") \
                .select("region") \
                .execute()
            
            # Extract unique regions
            all_regions = [client.get("region") for client in regions_response.data]
            regions = list(set(all_regions))
        
        # Get badge statistics for each region
        region_stats = []
        for region in regions:
            # Skip empty regions
            if not region:
                continue
                
            stats_response = supabase_admin \
                .rpc(
                    "get_region_badge_statistics",
                    {"region_name": region, "timeframe_param": timeframe}
                ) \
                .execute()
            
            if stats_response.data:
                region_data = stats_response.data[0]
                region_data["region_name"] = region
                region_stats.append(region_data)
        
        # Sort regions by badge count (descending)
        region_stats.sort(key=lambda x: x.get("total_badges", 0), reverse=True)
        
        # Get total stats across all regions
        total_clients = sum(region.get("total_clients", 0) for region in region_stats)
        total_badges = sum(region.get("total_badges", 0) for region in region_stats)
        avg_compliance = sum(region.get("compliance_rate", 0) * region.get("total_clients", 0) 
                            for region in region_stats) / total_clients if total_clients > 0 else 0
        
        # Get global weekly trends
        trends_response = supabase_admin \
            .rpc(
                "get_global_weekly_trends",
                {"weeks_count": 12}
            ) \
            .execute()
        
        weekly_trends = trends_response.data or []
        
        # Prepare context for the template
        context = {
            "regions": region_stats,
            "timeframe": timeframe,
            "total_regions": len(region_stats),
            "total_clients": total_clients,
            "total_badges": total_badges,
            "avg_compliance_rate": round(avg_compliance, 1),
            "weekly_trends": weekly_trends,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": str(uuid.uuid4())[:8]
        }
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"regions_comparison_{timeframe}_{timestamp}.pdf"
        
        # Generate the PDF
        output_path = generate_pdf(
            "regions_comparison_template.html", 
            context, 
            output_filename,
            css_files=["static/css/report_styles.css"]
        )
        
        logger.info(f"Generated regions comparison report: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating regions comparison report: {str(e)}")
        raise


async def get_region_reports(region=None):
    """
    List all reports for a region, or all region reports if no region is provided.
    
    Args:
        region (str, optional): The region to filter reports by
        
    Returns:
        list: List of report info dictionaries with filename and create date
    """
    from .pdf_generator import list_reports
    import os
    
    try:
        # Get all report files
        all_report_files = list_reports()
        
        # Filter for region reports
        if region:
            report_files = [f for f in all_report_files if f.startswith(f"region_{region}_")]
        else:
            report_files = [f for f in all_report_files if f.startswith("region_") or f.startswith("regions_comparison_")]
        
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
        logger.error(f"Error listing region reports: {str(e)}")
        return []
