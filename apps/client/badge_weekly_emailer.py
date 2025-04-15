"""
Weekly Badge Report Emailer

This module sends weekly badge status reports to clients.
It queries the Supabase database for posting activity,
calculates badge status, and sends personalized email reports
using SendGrid.
"""

import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

from fastapi import BackgroundTasks
from jinja2 import Environment, FileSystemLoader
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, MimeType

from core.supabase import supabase_admin_client
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Jinja2 environment for email templates
template_env = Environment(loader=FileSystemLoader("templates/emails"))

# SendGrid API key
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "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")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "notifications@locallift.com")


def get_weekly_badge_data(client_id: str) -> Dict[str, Any]:
    """
    Get badge data for a client for the current week.
    
    Args:
        client_id: The ID of the client
        
    Returns:
        Dictionary with badge data
    """
    # Get current ISO week
    current_week = datetime.now().isocalendar()
    week_id = f"{current_week[0]}-W{str(current_week[1]).zfill(2)}"
    
    # Get posts for the week
    response = supabase_admin_client \
        .from_("gmb_posts") \
        .select("*") \
        .eq("client_id", client_id) \
        .eq("week_id", week_id) \
        .execute()
    
    posts = response.data or []
    total = len(posts)
    compliant = sum(1 for p in posts if p.get("compliant") is True)
    
    # Calculate badge status
    badge_earned = total >= 5 and compliant >= 5
    remaining = max(0, 5 - compliant)
    
    return {
        "badge": badge_earned,
        "compliant": compliant,
        "total": total,
        "remaining": remaining,
        "remaining_plural": "" if remaining == 1 else "s"
    }


def get_client_data(client_id: str) -> Optional[Dict[str, Any]]:
    """
    Get client data from the database.
    
    Args:
        client_id: The ID of the client
        
    Returns:
        Dictionary with client data or None if client not found
    """
    response = supabase_admin_client \
        .from_("clients") \
        .select("id, name, email") \
        .eq("id", client_id) \
        .single() \
        .execute()
    
    return response.data


async def send_badge_email(client_id: str, force: bool = False) -> bool:
    """
    Send badge status email to a client.
    
    Args:
        client_id: The ID of the client
        force: If True, send email regardless of email settings
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        # Get client data
        client = get_client_data(client_id)
        if not client:
            logger.error(f"Client not found: {client_id}")
            return False
        
        # Get badge data
        badge_data = get_weekly_badge_data(client_id)
        
        # Prepare email context
        context = {
            "client_name": client["name"],
            "compliant": badge_data["compliant"],
            "total": badge_data["total"],
            "badge": badge_data["badge"],
            "remaining": badge_data["remaining"],
            "remaining_plural": badge_data["remaining_plural"],
            "dashboard_link": f"{settings.PUBLIC_URL}/dashboard"
        }
        
        # Render email template
        template = template_env.get_template("badge_weekly_report.html")
        html_content = template.render(**context)
        
        # Create email message
        message = Mail(
            from_email=Email(FROM_EMAIL),
            to_emails=To(client["email"]),
            subject="🏅 Your Weekly Posting Badge Report",
            html_content=Content(MimeType.html, html_content)
        )
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Log response
        status_code = response.status_code
        logger.info(f"Email sent to {client['email']} with status code {status_code}")
        
        # Record email in database
        supabase_admin_client \
            .from_("email_logs") \
            .insert({
                "client_id": client_id,
                "email_type": "weekly_badge_report",
                "status": "sent" if status_code == 202 else "failed",
                "metadata": {
                    "badge_earned": badge_data["badge"],
                    "compliant_posts": badge_data["compliant"],
                    "total_posts": badge_data["total"]
                }
            }) \
            .execute()
        
        return status_code == 202
        
    except Exception as e:
        logger.error(f"Error sending badge email to {client_id}: {str(e)}")
        return False


async def send_all_weekly_reports(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Send weekly badge reports to all active clients.
    
    Args:
        background_tasks: FastAPI background tasks object
        
    Returns:
        Dictionary with summary of emails sent
    """
    # Get all active clients
    response = supabase_admin_client \
        .from_("clients") \
        .select("id") \
        .eq("status", "active") \
        .eq("email_preferences.weekly_reports", True) \
        .execute()
    
    clients = response.data or []
    total_clients = len(clients)
    
    # Schedule sending emails in background
    for client in clients:
        background_tasks.add_task(send_badge_email, client["id"])
    
    return {
        "scheduled": total_clients,
        "message": f"Scheduled {total_clients} weekly badge reports for sending"
    }


# For manual testing
if __name__ == "__main__":
    import asyncio
    from fastapi import BackgroundTasks
    
    # Test sending email to a specific client
    # asyncio.run(send_badge_email("536f7e35-3cca-42ab-8aa3-6d63d68d952e", force=True))
    
    # Test sending emails to all clients
    # asyncio.run(send_all_weekly_reports(BackgroundTasks()))
