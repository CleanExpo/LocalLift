"""
Reports API Module

This module provides API endpoints for generating and accessing reports.
"""

import os
import logging
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Response, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from core.auth.auth_utils import get_admin_user, get_current_user
from . import client_report, region_report, internal_kpi_report
from .pdf_generator import list_reports, get_report_url, delete_report

# Configure logger
logger = logging.getLogger(__name__)

# Set up router
router = APIRouter()


@router.post("/api/reports/client/{client_id}")
async def generate_client_report(
    client_id: str,
    include_achievements: bool = True,
    background_tasks: BackgroundTasks = None,
    current_user = Depends(get_current_user)
):
    """
    Generate a PDF report for a specific client.
    
    Args:
        client_id: The client's unique identifier
        include_achievements: Whether to include achievement data
        background_tasks: Optional background tasks handler
        current_user: The authenticated user (from auth dependency)
        
    Returns:
        The URL for accessing the generated report
    """
    # Check if user has permission to access this client's data
    if current_user["id"] != client_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to generate this report"
        )
    
    try:
        # Generate in background if background_tasks provided
        if background_tasks:
            # Schedule report generation in background
            output_path_future = {"path": None}
            
            async def generate_in_background():
                try:
                    path = await client_report.create_client_report(client_id, include_achievements)
                    output_path_future["path"] = path
                except Exception as e:
                    logger.error(f"Background report generation failed: {str(e)}")
            
            background_tasks.add_task(generate_in_background)
            
            return {
                "status": "processing",
                "message": "Report generation started in the background. It will be available shortly."
            }
        
        # Otherwise generate immediately
        output_path = await client_report.create_client_report(client_id, include_achievements)
        filename = os.path.basename(output_path)
        url = get_report_url(filename)
        
        return {
            "status": "complete",
            "url": url,
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error generating client report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/api/reports/region/{region}")
async def generate_region_report(
    region: str,
    timeframe: str = "all",
    current_user = Depends(get_admin_user)
):
    """
    Generate a PDF report for a specific region.
    
    This endpoint requires admin privileges.
    
    Args:
        region: The region name
        timeframe: The time period to analyze (week, month, quarter, year, all)
        current_user: The authenticated admin user
        
    Returns:
        The URL for accessing the generated report
    """
    try:
        output_path = await region_report.create_region_report(region, timeframe)
        filename = os.path.basename(output_path)
        url = get_report_url(filename)
        
        return {
            "status": "complete",
            "url": url,
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error generating region report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/api/reports/regions-comparison")
async def generate_regions_comparison_report(
    regions: Optional[List[str]] = None,
    timeframe: str = "all",
    current_user = Depends(get_admin_user)
):
    """
    Generate a PDF report comparing multiple regions.
    
    This endpoint requires admin privileges.
    
    Args:
        regions: List of regions to include (optional, all regions if not provided)
        timeframe: The time period to analyze (week, month, quarter, year, all)
        current_user: The authenticated admin user
        
    Returns:
        The URL for accessing the generated report
    """
    try:
        output_path = await region_report.create_regions_comparison_report(regions, timeframe)
        filename = os.path.basename(output_path)
        url = get_report_url(filename)
        
        return {
            "status": "complete",
            "url": url,
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error generating regions comparison report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/api/reports/kpi")
async def generate_kpi_report(
    timeframe: str = "month",
    compare_previous: bool = True,
    current_user = Depends(get_admin_user)
):
    """
    Generate an internal KPI report.
    
    This endpoint requires admin privileges.
    
    Args:
        timeframe: The time period to analyze (week, month, quarter, year)
        compare_previous: Whether to include comparison with previous period
        current_user: The authenticated admin user
        
    Returns:
        The URL for accessing the generated report
    """
    try:
        output_path = await internal_kpi_report.create_kpi_report(timeframe, compare_previous)
        filename = os.path.basename(output_path)
        url = get_report_url(filename)
        
        return {
            "status": "complete",
            "url": url,
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error generating KPI report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/api/reports/executive-summary")
async def generate_executive_summary(
    current_user = Depends(get_admin_user)
):
    """
    Generate an executive summary report.
    
    This endpoint requires admin privileges.
    
    Args:
        current_user: The authenticated admin user
        
    Returns:
        The URL for accessing the generated report
    """
    try:
        output_path = await internal_kpi_report.create_executive_summary_report()
        filename = os.path.basename(output_path)
        url = get_report_url(filename)
        
        return {
            "status": "complete",
            "url": url,
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error generating executive summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/api/reports/client/{client_id}")
async def list_client_reports(
    client_id: str,
    current_user = Depends(get_current_user)
):
    """
    List all reports for a specific client.
    
    Args:
        client_id: The client's unique identifier
        current_user: The authenticated user
        
    Returns:
        List of reports for the client
    """
    # Check if user has permission to access this client's data
    if current_user["id"] != client_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access these reports"
        )
    
    try:
        reports = await client_report.get_client_reports(client_id)
        return reports
    
    except Exception as e:
        logger.error(f"Error listing client reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}"
        )


@router.get("/api/reports/region/{region}")
async def list_region_reports(
    region: str,
    current_user = Depends(get_admin_user)
):
    """
    List all reports for a specific region.
    
    This endpoint requires admin privileges.
    
    Args:
        region: The region name
        current_user: The authenticated admin user
        
    Returns:
        List of reports for the region
    """
    try:
        reports = await region_report.get_region_reports(region)
        return reports
    
    except Exception as e:
        logger.error(f"Error listing region reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}"
        )


@router.get("/api/reports/admin")
async def list_admin_reports(
    current_user = Depends(get_admin_user)
):
    """
    List all admin reports (KPI and executive reports).
    
    This endpoint requires admin privileges.
    
    Args:
        current_user: The authenticated admin user
        
    Returns:
        List of admin reports
    """
    try:
        reports = await internal_kpi_report.get_internal_reports()
        return reports
    
    except Exception as e:
        logger.error(f"Error listing admin reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}"
        )


@router.get("/exports/{filename}")
async def get_report(
    filename: str,
    current_user = Depends(get_current_user)
):
    """
    Get a specific report file.
    
    This endpoint checks permissions based on the report type.
    
    Args:
        filename: The report filename
        current_user: The authenticated user
        
    Returns:
        The report file as a download
    """
    file_path = os.path.join("exports", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions based on report type
    is_admin = current_user.get("is_admin", False)
    
    # Internal reports require admin privileges
    if (filename.startswith("internal_kpi_") or 
        filename.startswith("executive_summary_") or
        filename.startswith("regions_comparison_")):
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required for this report"
            )
    
    # Client reports require being the client or an admin
    elif filename.startswith("client_") or filename.startswith(current_user["id"]):
        client_id = filename.split("_")[0]
        if client_id != current_user["id"] and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this report"
            )
    
    # Region reports require admin privileges
    elif filename.startswith("region_"):
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required for this report"
            )
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


@router.delete("/api/reports/{filename}")
async def delete_report_file(
    filename: str,
    current_user = Depends(get_admin_user)
):
    """
    Delete a specific report file.
    
    This endpoint requires admin privileges.
    
    Args:
        filename: The report filename
        current_user: The authenticated admin user
        
    Returns:
        Success status
    """
    result = delete_report(filename)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or could not be deleted"
        )
    
    return {
        "status": "success",
        "message": f"Report {filename} deleted successfully"
    }


@router.post("/api/reports/cleanup")
async def cleanup_old_reports(
    days: int = 30,
    current_user = Depends(get_admin_user)
):
    """
    Delete reports older than a specified number of days.
    
    This endpoint requires admin privileges.
    
    Args:
        days: Age in days of reports to delete
        current_user: The authenticated admin user
        
    Returns:
        Number of reports deleted
    """
    from .pdf_generator import cleanup_old_reports
    
    count = cleanup_old_reports(days)
    
    return {
        "status": "success",
        "deleted_count": count,
        "message": f"Deleted {count} reports older than {days} days"
    }
