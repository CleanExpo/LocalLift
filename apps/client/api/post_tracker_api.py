"""
GMB Post Tracker API

API endpoints for the GMB post tracker dashboard widget.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json

# Import necessary models from core
from core.auth.router import get_current_user
from core.database.connection import get_db
from sqlalchemy.orm import Session

# Set up logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/post-tracker",
    tags=["post-tracker"],
    responses={404: {"description": "Not found"}}
)


@router.get("/{client_id}")
async def get_post_tracker_data(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get GMB post tracker data for a client
    
    Args:
        client_id: Client ID to get data for
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Dict containing post data, badge status, and compliance information
    """
    try:
        logger.info(f"Fetching post tracker data for client {client_id}")
        
        # In a real implementation, we would fetch this data from the database
        # or external APIs. For now, returning mock data.
        
        # Check if the user has permission to access this client's data
        # This would typically involve checking the user's role and permissions
        
        # Generate mock data
        post_data = generate_mock_post_data(client_id)
        badge_status = generate_mock_badge_status(client_id)
        compliance_data = generate_mock_compliance_data(client_id)
        
        return {
            "client_id": client_id,
            "last_updated": datetime.now().isoformat(),
            "post_engagement": post_data,
            "badge_status": badge_status,
            "compliance": compliance_data
        }
    
    except Exception as e:
        logger.error(f"Error fetching post tracker data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch post tracker data: {str(e)}"
        )


def generate_mock_post_data(client_id: str) -> Dict[str, Any]:
    """Generate mock post engagement data"""
    # In a real implementation, this would come from the GMB API or database
    
    now = datetime.now()
    
    return {
        "recent_posts": [
            {
                "id": f"{client_id}-post-1",
                "date": (now - timedelta(days=2)).isoformat(),
                "content": "Check out our latest offerings! We've added new services that our customers have been asking for.",
                "views": 245,
                "clicks": 37,
                "status": "published"
            },
            {
                "id": f"{client_id}-post-2",
                "date": (now - timedelta(days=7)).isoformat(),
                "content": "Special promotion this week only! Book an appointment today and get 15% off your first service.",
                "views": 189,
                "clicks": 42,
                "status": "published"
            },
            {
                "id": f"{client_id}-post-3",
                "date": (now - timedelta(days=14)).isoformat(),
                "content": "We're excited to announce extended hours starting next month. Now open evenings and weekends!",
                "views": 156,
                "clicks": 28,
                "status": "published"
            }
        ],
        "scheduled_posts": [
            {
                "id": f"{client_id}-post-4",
                "scheduled_date": (now + timedelta(days=3)).isoformat(),
                "content": "Join us for our upcoming workshop on industry best practices. Limited spots available!",
                "status": "scheduled"
            },
            {
                "id": f"{client_id}-post-5",
                "scheduled_date": (now + timedelta(days=10)).isoformat(),
                "content": "Holiday hours announcement: We'll be closed on the 25th, but open with extended hours before and after!",
                "status": "scheduled"
            }
        ],
        "engagement_trend": {
            "views": [120, 145, 210, 198, 245, 267, 230],
            "clicks": [18, 24, 35, 29, 37, 42, 38],
            "dates": [(now - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(7, 0, -1)]
        }
    }


def generate_mock_badge_status(client_id: str) -> Dict[str, Any]:
    """Generate mock badge status data"""
    # In a real implementation, this would come from the database
    
    return {
        "earned_badges": ["consistent_poster", "engagement_pro", "quick_responder"],
        "progress": {
            "local_expert": {
                "progress": 75,
                "requirements": "Respond to 10 more reviews to earn this badge",
                "next_level": "gold"
            },
            "content_creator": {
                "progress": 60,
                "requirements": "Post 4 more image posts to earn this badge",
                "next_level": "silver"
            }
        },
        "recent_badges": [
            {
                "name": "quick_responder",
                "earned_date": (datetime.now() - timedelta(days=5)).isoformat(),
                "level": "silver"
            }
        ]
    }


def generate_mock_compliance_data(client_id: str) -> Dict[str, Any]:
    """Generate mock compliance data"""
    # In a real implementation, this would come from the database
    
    now = datetime.now()
    
    return {
        "status": "good",
        "score": 92,
        "timeline": [
            {
                "date": (now - timedelta(days=30)).isoformat(),
                "score": 85,
                "events": ["Missing weekly post"]
            },
            {
                "date": (now - timedelta(days=20)).isoformat(),
                "score": 90,
                "events": ["Added business hours", "Updated services"]
            },
            {
                "date": (now - timedelta(days=10)).isoformat(),
                "score": 92,
                "events": ["Responded to all reviews"]
            }
        ],
        "recommendations": [
            "Add more photos to your business profile",
            "Consider posting weekly updates about your services"
        ]
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok", "service": "post-tracker-api"}
