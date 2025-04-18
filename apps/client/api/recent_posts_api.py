"""
Recent Posts API

This module provides API endpoints for retrieving recent posts
for the post notification system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from core.config import settings
from core.database.supabase import get_supabase_client

router = APIRouter()

@router.get("/api/posts/recent", response_model=List[Dict[str, Any]])
async def get_recent_posts():
    """
    Get posts created in the last hour.
    
    Returns a list of recent posts with their details.
    """
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Calculate timestamp for 1 hour ago
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        iso_timestamp = one_hour_ago.isoformat()
        
        # Query posts created in the last hour
        response = supabase.table('posts').select('*').gte('created_at', iso_timestamp).execute()
        
        if hasattr(response, 'error') and response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching recent posts: {response.error.message}"
            )
        
        # Return the posts
        return response.data
        
    except Exception as e:
        # For development/testing, return mock data if database is not available
        if settings.DEBUG:
            # Generate mock data
            mock_posts = [
                {
                    "id": "1",
                    "title": "New Local Business Spotlight",
                    "url": "/posts/1",
                    "created_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "author_id": "user1",
                    "author_name": "Jane Smith"
                },
                {
                    "id": "2",
                    "title": "Weekly Marketing Tips",
                    "url": "/posts/2",
                    "created_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                    "author_id": "user2",
                    "author_name": "John Doe"
                },
                {
                    "id": "3",
                    "title": "Upcoming Community Event",
                    "url": "/posts/3",
                    "created_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                    "author_id": "user3",
                    "author_name": "Alice Johnson"
                }
            ]
            return mock_posts
        
        # In production, propagate the error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recent posts: {str(e)}"
        )
