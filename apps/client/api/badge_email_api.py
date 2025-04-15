"""
Badge Email API

This module provides API endpoints for sending weekly badge status emails
to clients. It includes endpoints for triggering emails for all clients
as well as sending a test email to a specific client.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Dict, Any, Optional

from core.config import settings
from apps.client.badge_weekly_emailer import send_badge_email, send_all_weekly_reports

router = APIRouter()

# API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)


async def verify_api_key(api_key: str = Depends(api_key_header)) -> bool:
    """
    Verify that the provided API key is valid.
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return True


@router.post("/api/admin/badge-reports/send-all", response_model=Dict[str, Any])
async def trigger_all_badge_reports(
    background_tasks: BackgroundTasks,
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Trigger sending badge reports to all active clients.
    
    This endpoint is intended to be called by a scheduled job
    (e.g., weekly cron job) to send reports to all clients who
    have opted-in to weekly reports.
    
    Requires API key authentication.
    """
    result = await send_all_weekly_reports(background_tasks)
    return result


@router.post("/api/admin/badge-reports/test/{client_id}", response_model=Dict[str, Any])
async def send_test_badge_report(
    client_id: str,
    force: bool = True,
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Send a test badge report to a specific client.
    
    Args:
        client_id: The ID of the client to send the report to
        force: If True, override client email preferences
        
    Requires API key authentication.
    """
    success = await send_badge_email(client_id, force=force)
    
    if success:
        return {
            "status": "success",
            "message": f"Test badge report sent to client {client_id}"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test badge report to client {client_id}"
        )


@router.post("/api/webhooks/scheduled-tasks/weekly-badge-reports")
async def webhook_weekly_badge_reports(
    background_tasks: BackgroundTasks,
    webhook_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    Webhook endpoint for scheduled weekly badge reports.
    
    This endpoint is designed to be called by external schedulers
    like Railway cron jobs, Vercel cron, or other scheduling services.
    
    If webhook_secret is configured in settings, it will be required
    for authentication.
    """
    # Optional webhook secret authentication
    if settings.WEBHOOK_SECRET and webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret"
        )
    
    result = await send_all_weekly_reports(background_tasks)
    return result
