"""
Post Tracker Models

This module provides a unified import for all GMB post tracking related models
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

# Re-export GmbPost and PostTemplate models
from .gmb_post import GmbPost
from .post_template import PostTemplate

# Additional model definitions can be added here if needed

# Constants
POST_STATUS_DRAFT = "draft"
POST_STATUS_SCHEDULED = "scheduled"
POST_STATUS_PUBLISHED = "published"
POST_STATUS_FAILED = "failed"

POST_STATUS_CHOICES = [
    POST_STATUS_DRAFT,
    POST_STATUS_SCHEDULED,
    POST_STATUS_PUBLISHED,
    POST_STATUS_FAILED
]

# Utility functions for post tracker models
def get_post_status_display(status: str) -> str:
    """
    Convert status code to display name
    
    Args:
        status: Status code
        
    Returns:
        Display name for status
    """
    status_map = {
        POST_STATUS_DRAFT: "Draft",
        POST_STATUS_SCHEDULED: "Scheduled",
        POST_STATUS_PUBLISHED: "Published",
        POST_STATUS_FAILED: "Failed"
    }
    return status_map.get(status, status.capitalize())


def create_post_from_template(template: PostTemplate, client_id: str, scheduled_date: datetime) -> GmbPost:
    """
    Create a new GmbPost from a template
    
    Args:
        template: PostTemplate to use
        client_id: Client ID for the post
        scheduled_date: Date to schedule the post
        
    Returns:
        New GmbPost instance (unsaved)
    """
    from uuid import uuid4
    
    # Create post with template content
    post = GmbPost(
        id=str(uuid4()),
        client_id=client_id,
        post_id=f"draft-{uuid4()}",
        content=template.content_template,
        scheduled_date=scheduled_date,
        status=POST_STATUS_DRAFT,
        metrics={},
        last_updated=datetime.utcnow()
    )
    
    return post


# Model type hints for better IDE support
__all__ = [
    'GmbPost',
    'PostTemplate',
    'POST_STATUS_DRAFT',
    'POST_STATUS_SCHEDULED', 
    'POST_STATUS_PUBLISHED',
    'POST_STATUS_FAILED',
    'POST_STATUS_CHOICES',
    'get_post_status_display',
    'create_post_from_template'
]
