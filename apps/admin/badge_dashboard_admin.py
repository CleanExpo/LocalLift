"""
Badge Dashboard Admin

This module provides the controller and view logic for the badge admin dashboard.
It renders the badge dashboard and handles admin-level operations related to
the badge system.
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from core.config import get_settings
from core.supabase import supabase_admin_client

# Set up router
router = APIRouter()

# Templates
templates = Jinja2Templates(directory="templates")

# Settings
settings = get_settings()


@router.get("/admin/badges", response_class=HTMLResponse)
async def badge_admin_dashboard(request: Request):
    """
    Render the badge admin dashboard.
    
    This dashboard provides a comprehensive interface for managing
    and analyzing the badge system.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        HTML response with the rendered template
    """
    return templates.TemplateResponse(
        "badge_admin.html",
        {
            "request": request,
            "title": "Badge System Administration",
            "active_tab": "badges"
        }
    )


@router.get("/admin/badges/export/{format}")
async def export_badge_data(
    format: str,
    timeframe: str = "all"
):
    """
    Export badge data in various formats (CSV, Excel, JSON).
    
    Args:
        format: The export format (csv, excel, json)
        timeframe: The time period to export (week, month, quarter, year, all)
        
    Returns:
        Downloadable file in the requested format
    """
    # Validate format
    if format not in ["csv", "excel", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Use csv, excel, or json."
        )
    
    # Get badge data for export
    try:
        # Get badge leaderboard data
        leaderboard_response = supabase_admin_client \
            .rpc(
                "get_badge_leaderboard", 
                {"timeframe": timeframe, "limit_count": 1000}
            ) \
            .execute()
        
        # Get badge history data
        history_query = supabase_admin_client.from_("badge_history").select("*")
        
        # Apply timeframe filter if needed
        if timeframe != "all":
            # Calculate start date based on timeframe
            import datetime
            now = datetime.datetime.now()
            
            if timeframe == "week":
                # Current week
                week_id = f"{now.isocalendar()[0]}-W{str(now.isocalendar()[1]).zfill(2)}"
                history_query = history_query.eq("week_id", week_id)
            elif timeframe == "month":
                # Current month
                start_of_month = datetime.datetime(now.year, now.month, 1)
                start_week = start_of_month.isocalendar()
                start_week_id = f"{start_week[0]}-W{str(start_week[1]).zfill(2)}"
                history_query = history_query.gte("week_id", start_week_id)
            elif timeframe == "quarter":
                # Current quarter
                quarter_month = (now.month - 1) // 3 * 3 + 1
                start_of_quarter = datetime.datetime(now.year, quarter_month, 1)
                start_week = start_of_quarter.isocalendar()
                start_week_id = f"{start_week[0]}-W{str(start_week[1]).zfill(2)}"
                history_query = history_query.gte("week_id", start_week_id)
            elif timeframe == "year":
                # Current year
                history_query = history_query.like("week_id", f"{now.year}-%")
        
        history_response = history_query.execute()
        
        # Combine data for export
        export_data = {
            "leaderboard": leaderboard_response.data,
            "history": history_response.data,
            "timeframe": timeframe,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
        # Generate export file
        if format == "json":
            import json
            from fastapi.responses import JSONResponse
            
            return JSONResponse(
                content=export_data,
                headers={
                    "Content-Disposition": f"attachment; filename=badge_data_{timeframe}.json"
                }
            )
        
        elif format == "csv":
            import csv
            import io
            from fastapi.responses import StreamingResponse
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write leaderboard data
            writer.writerow([
                "Rank", "Client ID", "Client Name", "Region", 
                "Badges Earned", "Compliance Rate", "Total Weeks"
            ])
            
            for entry in leaderboard_response.data:
                writer.writerow([
                    entry.get("rank"),
                    entry.get("client_id"),
                    entry.get("client_name"),
                    entry.get("region"),
                    entry.get("badges_earned"),
                    f"{entry.get('compliance_rate')}%",
                    entry.get("total_weeks")
                ])
            
            # Add a blank row
            writer.writerow([])
            
            # Write history data
            writer.writerow([
                "Client ID", "Week ID", "Badge Earned", 
                "Compliant Posts", "Total Posts"
            ])
            
            for entry in history_response.data:
                writer.writerow([
                    entry.get("client_id"),
                    entry.get("week_id"),
                    "Yes" if entry.get("earned") else "No",
                    entry.get("compliant"),
                    entry.get("total")
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=badge_data_{timeframe}.csv"
                }
            )
        
        elif format == "excel":
            import io
            import pandas as pd
            from fastapi.responses import StreamingResponse
            
            # Convert leaderboard data to DataFrame
            leaderboard_df = pd.DataFrame(leaderboard_response.data)
            
            # Convert history data to DataFrame
            history_df = pd.DataFrame(history_response.data)
            
            # Create Excel file with multiple sheets
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                leaderboard_df.to_excel(writer, sheet_name='Leaderboard', index=False)
                history_df.to_excel(writer, sheet_name='History', index=False)
                
                # Get workbook and add a summary sheet
                workbook = writer.book
                summary_sheet = workbook.add_worksheet('Summary')
                
                # Write summary info
                summary_sheet.write(0, 0, 'Badge Data Export')
                summary_sheet.write(1, 0, f'Timeframe: {timeframe}')
                summary_sheet.write(2, 0, f'Generated at: {datetime.datetime.now().isoformat()}')
                summary_sheet.write(4, 0, f'Total clients: {len(set(history_df["client_id"]))}')
                summary_sheet.write(5, 0, f'Total weeks tracked: {len(set(history_df["week_id"]))}')
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=badge_data_{timeframe}.xlsx"
                }
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export badge data: {str(e)}"
        )
