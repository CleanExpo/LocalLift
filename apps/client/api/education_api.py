"""
Education API

This module provides API endpoints for the client Education Hub functionality.
It enables access to educational content, progress tracking, and personalized recommendations.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from core.database.session import get_db
from core.auth.dependencies import get_current_user
from apps.client.education_hub_client import EducationHub, get_education_hub_controller
from apps.client.models.lesson import Lesson
from apps.client.models.progress import Progress

# Create router
router = APIRouter(
    prefix="/api/client/education",
    tags=["client", "education"],
    responses={404: {"description": "Not found"}},
)


@router.get("/lessons")
async def get_lessons(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    format_type: Optional[str] = Query(None, description="Filter by format type"),
    limit: int = Query(20, description="Maximum number of lessons to retrieve"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get available educational content with optional filtering.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    education_hub = get_education_hub_controller(db)
    
    try:
        lessons = education_hub.get_available_lessons(
            category=category,
            difficulty=difficulty,
            format_type=format_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "count": len(lessons),
            "lessons": lessons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving lessons: {str(e)}")


@router.get("/lessons/{slug}")
async def get_lesson(
    slug: str = Path(..., description="Lesson slug"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed information for a specific lesson by its slug.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    education_hub = get_education_hub_controller(db)
    
    lesson = education_hub.get_lesson_by_slug(slug)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Get the client's progress on this lesson if any
    progress = db.query(Progress).filter(
        Progress.client_id == current_user.id,
        Progress.lesson_id == lesson["id"]
    ).first()
    
    # If found, add progress data to the lesson
    if progress:
        lesson["progress"] = progress.to_dict()
    else:
        lesson["progress"] = None
    
    # Increment view count
    lesson_obj = db.query(Lesson).filter(Lesson.id == lesson["id"]).first()
    if lesson_obj:
        lesson_obj.increment_view_count()
        db.commit()
    
    return {
        "status": "success",
        "lesson": lesson
    }


@router.get("/progress")
async def get_client_progress(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the client's learning progress across all lessons.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    education_hub = get_education_hub_controller(db)
    
    try:
        progress = education_hub.get_client_progress(current_user.id)
        
        return {
            "status": "success",
            "progress": progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving progress: {str(e)}")


@router.post("/progress/{lesson_id}")
async def update_lesson_progress(
    lesson_id: str = Path(..., description="ID of the lesson to update progress for"),
    status: Optional[str] = Query(None, description="New lesson status"),
    progress_percentage: Optional[float] = Query(None, description="New progress percentage (0-100)"),
    bookmarked: Optional[bool] = Query(None, description="Bookmark status"),
    notes: Optional[str] = Query(None, description="User notes about the lesson"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update the client's progress on a specific lesson.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    education_hub = get_education_hub_controller(db)
    
    try:
        updated_progress = education_hub.update_lesson_progress(
            client_id=current_user.id,
            lesson_id=lesson_id,
            status=status,
            progress_percentage=progress_percentage,
            bookmarked=bookmarked,
            notes=notes
        )
        
        # If marked as completed, update the lesson completion count
        if status == "completed" or (progress_percentage is not None and progress_percentage == 100):
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                lesson.increment_completion_count()
                db.commit()
        
        return {
            "status": "success",
            "message": "Progress updated successfully",
            "progress": updated_progress
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")


@router.post("/progress/{lesson_id}/time")
async def track_time_spent(
    lesson_id: str = Path(..., description="ID of the lesson"),
    seconds: int = Query(..., description="Number of seconds spent on the lesson"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Track time spent on a specific lesson.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if seconds < 0:
        raise HTTPException(status_code=400, detail="Time spent cannot be negative")
        
    # Get or create progress record
    progress = (
        db.query(Progress)
        .filter(
            Progress.client_id == current_user.id,
            Progress.lesson_id == lesson_id
        )
        .first()
    )
    
    if not progress:
        # Verify the lesson exists
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
            
        # Create new progress record
        progress = Progress(
            id=str(uuid.uuid4()),
            client_id=current_user.id,
            lesson_id=lesson_id,
            status="in_progress",
            progress_percentage=0,
            last_accessed=datetime.utcnow(),
            bookmarked=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(progress)
    
    # Add time spent
    progress.time_spent_seconds += seconds
    progress.last_accessed = datetime.utcnow()
    progress.updated_at = datetime.utcnow()
    
    # If not started, update status to in progress
    if progress.status == "not_started":
        progress.status = "in_progress"
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Time tracked successfully",
        "time_spent_total": progress.time_spent_seconds
    }


@router.post("/lessons/{lesson_id}/rating")
async def rate_lesson(
    lesson_id: str = Path(..., description="ID of the lesson to rate"),
    rating: int = Query(..., description="Rating (1-5)"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Rate a lesson on a scale of 1-5.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Get the lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    # Add rating to the lesson
    lesson.add_rating(rating)
    
    # Update the progress record with the rating if it exists
    progress = (
        db.query(Progress)
        .filter(
            Progress.client_id == current_user.id,
            Progress.lesson_id == lesson_id
        )
        .first()
    )
    
    if progress:
        progress.rating = rating
        progress.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Lesson rated successfully",
        "new_average_rating": lesson.average_rating,
        "rating_count": lesson.rating_count
    }


@router.get("/recommended")
async def get_recommended_lessons(
    limit: int = Query(5, description="Maximum number of recommendations"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get personalized lesson recommendations for the client.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    education_hub = get_education_hub_controller(db)
    
    try:
        recommendations = education_hub.get_recommended_lessons(
            client_id=current_user.id,
            limit=limit
        )
        
        return {
            "status": "success",
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@router.get("/categories")
async def get_lesson_categories(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get all lesson categories with counts.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    education_hub = get_education_hub_controller(db)
    
    try:
        categories = education_hub.get_lesson_categories()
        
        return {
            "status": "success",
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")
