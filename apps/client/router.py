"""
Client API router for Local Lift application.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.router import get_current_active_user
from core.auth.schemas import UserRead, UserUpdate
from core.database.connection import get_db

router = APIRouter()


# Profile Management
@router.get("/profile", response_model=UserRead)
async def get_profile(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current client's profile.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserRead: The client's profile
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    return current_user


@router.put("/profile", response_model=UserRead)
async def update_profile(
    user_update: UserUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current client's profile.
    
    Args:
        user_update: Updated profile data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserRead: The updated profile
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # Ensure client can't change their role
    if user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change role"
        )
    
    # This is a placeholder - in a real implementation, you would update the user in the database
    
    # For now, we'll simulate profile update
    updated_user = UserRead(
        id=current_user.id,
        email=user_update.email or current_user.email,
        name=user_update.name or current_user.name,
        role=current_user.role,
        region_id=current_user.region_id,
        permissions=current_user.permissions
    )
    
    return updated_user


# GMB Engagement
@router.get("/gmb/tasks", response_model=List[dict])
async def get_gmb_tasks(
    status: Optional[str] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get GMB engagement tasks for the client.
    
    Args:
        status: Filter tasks by status (pending, completed, overdue)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of GMB tasks
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch tasks from the database
    
    # For now, we'll simulate GMB tasks
    tasks = [
        {
            "id": 1,
            "title": "Respond to Google reviews",
            "description": "Respond to new 3-star review from John Smith",
            "status": "pending",
            "due_date": "2025-04-20T23:59:59Z",
            "points": 10
        },
        {
            "id": 2,
            "title": "Update business hours",
            "description": "Verify and update holiday hours for upcoming season",
            "status": "pending",
            "due_date": "2025-04-18T23:59:59Z",
            "points": 5
        },
        {
            "id": 3,
            "title": "Add new service photos",
            "description": "Upload at least 3 new photos showcasing recent work",
            "status": "completed",
            "completed_date": "2025-04-10T14:30:00Z",
            "points": 15
        }
    ]
    
    # Apply status filter if provided
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    return tasks


@router.post("/gmb/tasks/{task_id}/complete", response_model=dict)
async def complete_gmb_task(
    task_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a GMB task as completed.
    
    Args:
        task_id: The ID of the task to complete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Updated task with earned points
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # This is a placeholder - in a real implementation, you would update the task in the database
    
    # For now, we'll simulate task completion
    if task_id not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or already completed"
        )
    
    task = {
        "id": task_id,
        "title": "Respond to Google reviews" if task_id == 1 else "Update business hours",
        "status": "completed",
        "completed_date": "2025-04-14T21:30:00Z",
        "points_earned": 10 if task_id == 1 else 5,
        "message": "Task completed successfully"
    }
    
    return task


# Courses and Certification
@router.get("/courses", response_model=List[dict])
async def get_available_courses(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get available courses for the client.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of available courses
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch courses from the database
    
    # For now, we'll simulate courses
    courses = [
        {
            "id": 1,
            "title": "GMB Optimization Fundamentals",
            "description": "Learn the basics of optimizing your Google My Business listing",
            "modules": 5,
            "estimated_duration": "2 hours",
            "certification": True,
            "enrolled": True,
            "progress": 60,
            "points": 50
        },
        {
            "id": 2,
            "title": "Advanced Review Management",
            "description": "Strategies for handling negative reviews and maximizing positive feedback",
            "modules": 3,
            "estimated_duration": "1.5 hours",
            "certification": True,
            "enrolled": False,
            "progress": 0,
            "points": 40
        },
        {
            "id": 3,
            "title": "Local SEO Best Practices",
            "description": "Optimize your local search presence beyond GMB",
            "modules": 7,
            "estimated_duration": "3 hours",
            "certification": True,
            "enrolled": False,
            "progress": 0,
            "points": 75
        }
    ]
    
    return courses


@router.post("/courses/{course_id}/enroll", response_model=dict)
async def enroll_in_course(
    course_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enroll in a course.
    
    Args:
        course_id: The ID of the course to enroll in
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Enrollment confirmation
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # This is a placeholder - in a real implementation, you would handle enrollment in the database
    
    # For now, we'll simulate enrollment
    if course_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Simulate already enrolled in course 1
    if course_id == 1:
        return {
            "message": "Already enrolled in this course",
            "course_id": course_id,
            "progress": 60
        }
    
    return {
        "message": "Successfully enrolled in course",
        "course_id": course_id,
        "progress": 0,
        "next_steps": "Navigate to the course content to begin learning"
    }


@router.get("/certifications", response_model=List[dict])
async def get_certifications(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get client's earned certifications.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of earned certifications
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch certifications from the database
    
    # For now, we'll simulate certifications
    certifications = [
        {
            "id": 1,
            "title": "GMB Essentials Certified",
            "issued_date": "2025-03-15T10:00:00Z",
            "course_id": 1,
            "expires": "2026-03-15T10:00:00Z",
            "badge_url": "/badges/gmb-essentials.png"
        }
    ]
    
    return certifications


# Dashboard
@router.get("/dashboard", response_model=dict)
async def get_dashboard(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get client dashboard data.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Dashboard data
    """
    # Check if user is a client
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to client users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch dashboard data from the database
    
    # For now, we'll simulate dashboard data
    dashboard = {
        "points": 875,
        "rank": 3,
        "region_rank": 1,
        "completed_tasks": 42,
        "pending_tasks": 2,
        "certificates": 1,
        "courses_in_progress": 1,
        "recent_achievements": [
            {
                "id": 1,
                "title": "GMB Superstar",
                "description": "Completed 10 GMB tasks in a single week",
                "date_earned": "2025-04-07T16:45:00Z",
                "points": 50
            },
            {
                "id": 2,
                "title": "First Certificate",
                "description": "Earned your first certification",
                "date_earned": "2025-03-15T10:00:00Z",
                "points": 100
            }
        ],
        "recent_activities": [
            {
                "id": 1,
                "activity": "Completed GMB task: Add new service photos",
                "timestamp": "2025-04-10T14:30:00Z",
                "points": 15
            },
            {
                "id": 2,
                "activity": "Completed Module 3 of GMB Optimization Fundamentals",
                "timestamp": "2025-04-05T11:15:00Z",
                "points": 10
            }
        ],
        "leaderboard_position": {
            "movement": "+2",
            "next_milestone": 25,
            "points_to_next_rank": 125
        }
    }
    
    return dashboard
