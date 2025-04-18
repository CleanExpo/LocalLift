"""
Mock Posts API

This module provides API endpoints for creating mock posts
for testing the post notification system.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/api/mock/create-post", response_model=Dict[str, Any])
async def create_mock_post(title: str = "New Post"):
    """
    Create a mock post for testing the notification system.
    
    This endpoint is only available in development mode.
    """
    try:
        # Generate a unique ID for the post
        post_id = str(uuid.uuid4())
        
        # Create a mock post
        mock_post = {
            "id": post_id,
            "title": title,
            "url": f"/posts/{post_id}",
            "created_at": datetime.utcnow().isoformat(),
            "author_id": "test-user",
            "author_name": "Test User"
        }
        
        # In a real implementation, this would save to the database
        # For now, we just return the mock post
        
        return {
            "status": "success",
            "message": "Mock post created successfully",
            "post": mock_post
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mock post: {str(e)}"
        )
