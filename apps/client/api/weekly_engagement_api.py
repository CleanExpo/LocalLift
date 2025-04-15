"""
Weekly Engagement API

This module provides API endpoints for generating and accessing weekly engagement reports.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from core.database.session import get_db
from core.auth.dependencies import get_current_user
from apps.client.report_weekly_engagement import WeeklyEngagementReport, get_report_controller
from apps.client.models.engagement_record import EngagementRecord

# Create router
router = APIRouter(
    prefix="/api/client/engagement-reports",
    tags=["client", "engagement", "reports"],
    responses={404: {"description": "Not found"}},
)


@router.get("/generate")
async def generate_weekly_report(
    week_number: Optional[int] = Query(None, description="Week number (1-52)"),
    year: Optional[int] = Query(None, description="Year for the report"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a new weekly engagement report for the current user.
    If week number and year are not provided, the current week will be used.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    report_controller = get_report_controller(db)
    
    try:
        report = report_controller.generate_weekly_report(
            client_id=current_user.id,
            week_number=week_number,
            year=year
        )
        
        return {
            "status": "success",
            "message": "Report generated successfully",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/")
async def get_reports(
    limit: int = Query(10, description="Maximum number of reports to retrieve"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get historical reports for the current user.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    report_controller = get_report_controller(db)
    
    try:
        reports = report_controller.get_historical_reports(
            client_id=current_user.id,
            limit=limit
        )
        
        return {
            "status": "success",
            "message": f"Retrieved {len(reports)} reports",
            "reports": reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")


@router.get("/{report_id}")
async def get_report_detail(
    report_id: str = Path(..., description="ID of the report to retrieve"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed information for a specific report.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    # Query the database for the report
    report = db.query(EngagementRecord).filter(
        EngagementRecord.id == report_id,
        EngagementRecord.client_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Mark the report as viewed if not already
    if not report.viewed:
        report_controller = get_report_controller(db)
        report_controller.mark_report_viewed(report_id)
    
    return {
        "status": "success",
        "report": report.to_dict()
    }


@router.post("/{report_id}/viewed")
async def mark_report_viewed(
    report_id: str = Path(..., description="ID of the report to mark as viewed"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Mark a report as viewed.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    report_controller = get_report_controller(db)
    
    if report_controller.mark_report_viewed(report_id):
        return {
            "status": "success",
            "message": "Report marked as viewed"
        }
    else:
        raise HTTPException(status_code=404, detail="Report not found")
