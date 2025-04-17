"""
Gamification API router for Local Lift application.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session

from core.auth.router import get_current_active_user
from core.auth.schemas import UserRead
from core.database.connection import get_db

router = APIRouter()


# Points Management
@router.get("/points/{user_id}", response_model=dict)
async def get_user_points(
    user_id: int = Path(..., ge=1),
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get points for a specific user.
    
    Args:
        user_id: The ID of the user
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Points information
    """
    # Check permissions - users can view their own points, admins can view anyone's
    if current_user.id != user_id and current_user.role not in ["admin", "regional_manager", "franchise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # This is a placeholder - in a real implementation, you would fetch points from the database
    
    # For now, we'll simulate points data
    points_data = {
        "user_id": user_id,
        "total_points": 875,
        "level": 8,
        "next_level_points": 125,
        "percentile": 92,
        "rank": {
            "overall": 42,
            "region": 3,
            "franchise": 1
        },
        "recent_points": [
            {
                "id": 123,
                "amount": 10,
                "action": "Complete GMB task: Respond to review",
                "timestamp": "2025-04-14T14:30:00Z"
            },
            {
                "id": 122,
                "amount": 5,
                "action": "Daily login streak: 7 days",
                "timestamp": "2025-04-14T09:15:00Z"
            },
            {
                "id": 121,
                "amount": 25,
                "action": "Complete module in GMB Optimization course",
                "timestamp": "2025-04-13T16:45:00Z"
            }
        ],
        "points_breakdown": {
            "gmb_tasks": 350,
            "courses": 275,
            "certifications": 150,
            "login_streaks": 65,
            "bonuses": 35
        }
    }
    
    return points_data


@router.post("/points/{user_id}/award", response_model=dict, status_code=status.HTTP_201_CREATED)
async def award_points(
    user_id: int,
    points_data: dict,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Award points to a user.
    
    Args:
        user_id: The ID of the user
        points_data: The points data (amount, action, etc.)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Updated points information
    """
    # Check permissions - only admin, regional_manager, or franchise can award points
    if current_user.role not in ["admin", "regional_manager", "franchise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # This is a placeholder - in a real implementation, you would add points in the database
    
    # For now, we'll simulate awarding points
    amount = points_data.get("amount", 0)
    action = points_data.get("action", "Unspecified action")
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Points amount must be positive"
        )
    
    # Return updated points
    result = {
        "user_id": user_id,
        "points_awarded": amount,
        "action": action,
        "timestamp": "2025-04-14T20:00:00Z",
        "new_total": 885,  # Previous + amount
        "previous_total": 875,
        "level": 8,
        "next_level_points": 115,  # Updated based on new total
        "message": f"Successfully awarded {amount} points for {action}"
    }
    
    return result


# Achievements
@router.get("/achievements", response_model=List[dict])
async def get_all_achievements(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all available achievements.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of all achievements
    """
    # This is a placeholder - in a real implementation, you would fetch achievements from the database
    
    # For now, we'll simulate achievements data
    achievements = [
        {
            "id": 1,
            "name": "GMB Superstar",
            "description": "Complete 10 GMB tasks in a single week",
            "points": 50,
            "category": "GMB",
            "icon": "star.png",
            "difficulty": "medium"
        },
        {
            "id": 2,
            "name": "First Certificate",
            "description": "Earn your first certification",
            "points": 100,
            "category": "Education",
            "icon": "certificate.png",
            "difficulty": "easy"
        },
        {
            "id": 3,
            "name": "Perfect Attendance",
            "description": "Log in every day for 30 consecutive days",
            "points": 75,
            "category": "Engagement",
            "icon": "calendar.png",
            "difficulty": "hard"
        },
        {
            "id": 4,
            "name": "Five-Star Service",
            "description": "Maintain a 5-star GMB rating for 3 months",
            "points": 150,
            "category": "GMB",
            "icon": "stars.png",
            "difficulty": "hard"
        },
        {
            "id": 5,
            "name": "Speedy Response",
            "description": "Respond to 20 reviews within 24 hours of posting",
            "points": 75,
            "category": "GMB",
            "icon": "clock.png",
            "difficulty": "medium"
        }
    ]
    
    return achievements


@router.get("/achievements/{user_id}", response_model=dict)
async def get_user_achievements(
    user_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get achievements for a specific user.
    
    Args:
        user_id: The ID of the user
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: User achievements information
    """
    # Check permissions - users can view their own achievements, admins can view anyone's
    if current_user.id != user_id and current_user.role not in ["admin", "regional_manager", "franchise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # This is a placeholder - in a real implementation, you would fetch user achievements from the database
    
    # For now, we'll simulate user achievements data
    user_achievements = {
        "user_id": user_id,
        "completed_count": 2,
        "total_available": 5,
        "total_points_earned": 150,
        "completed_achievements": [
            {
                "id": 1,
                "name": "GMB Superstar",
                "description": "Complete 10 GMB tasks in a single week",
                "points": 50,
                "category": "GMB",
                "icon": "star.png",
                "earned_date": "2025-04-07T16:45:00Z"
            },
            {
                "id": 2,
                "name": "First Certificate",
                "description": "Earn your first certification",
                "points": 100,
                "category": "Education",
                "icon": "certificate.png",
                "earned_date": "2025-03-15T10:00:00Z"
            }
        ],
        "in_progress_achievements": [
            {
                "id": 3,
                "name": "Perfect Attendance",
                "description": "Log in every day for 30 consecutive days",
                "points": 75,
                "category": "Engagement",
                "icon": "calendar.png",
                "progress": {
                    "current": 12,
                    "target": 30,
                    "percentage": 40
                }
            },
            {
                "id": 5,
                "name": "Speedy Response",
                "description": "Respond to 20 reviews within 24 hours of posting",
                "points": 75,
                "category": "GMB",
                "icon": "clock.png",
                "progress": {
                    "current": 8,
                    "target": 20,
                    "percentage": 40
                }
            }
        ]
    }
    
    return user_achievements


# Levels & Progression
@router.get("/levels", response_model=List[dict])
async def get_level_system(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of the level progression system.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: Level system information
    """
    # This is a placeholder - in a real implementation, you would fetch level data from the database
    
    # For now, we'll simulate level system data
    levels = [
        {
            "level": 1,
            "name": "Rookie",
            "min_points": 0,
            "max_points": 99,
            "icon": "level1.png",
            "benefits": ["Basic GMB tools access"]
        },
        {
            "level": 2,
            "name": "Novice",
            "min_points": 100,
            "max_points": 249,
            "icon": "level2.png",
            "benefits": ["Basic GMB tools access", "Weekly performance reports"]
        },
        {
            "level": 3,
            "name": "Apprentice",
            "min_points": 250,
            "max_points": 499,
            "icon": "level3.png",
            "benefits": ["Basic GMB tools access", "Weekly performance reports", "Basic course access"]
        },
        {
            "level": 4,
            "name": "Practitioner",
            "min_points": 500,
            "max_points": 749,
            "icon": "level4.png",
            "benefits": ["Advanced GMB tools access", "Weekly performance reports", "Basic course access"]
        },
        {
            "level": 5,
            "name": "Expert",
            "min_points": 750,
            "max_points": 999,
            "icon": "level5.png",
            "benefits": ["Advanced GMB tools access", "Daily performance reports", "Full course access"]
        },
        {
            "level": 6,
            "name": "Master",
            "min_points": 1000,
            "max_points": 1499,
            "icon": "level6.png",
            "benefits": ["Advanced GMB tools access", "Real-time performance dashboard", "Full course access", "Priority support"]
        },
        {
            "level": 7,
            "name": "Grandmaster",
            "min_points": 1500,
            "max_points": 1999,
            "icon": "level7.png",
            "benefits": ["Advanced GMB tools access", "Real-time performance dashboard", "Full course access", "Priority support", "Custom reporting"]
        },
        {
            "level": 8,
            "name": "Legend",
            "min_points": 2000,
            "max_points": 2999,
            "icon": "level8.png",
            "benefits": ["Advanced GMB tools access", "Real-time performance dashboard", "Full course access", "Priority support", "Custom reporting", "Beta feature access"]
        },
        {
            "level": 9,
            "name": "Champion",
            "min_points": 3000,
            "max_points": 3999,
            "icon": "level9.png",
            "benefits": ["Advanced GMB tools access", "Real-time performance dashboard", "Full course access", "Priority support", "Custom reporting", "Beta feature access", "Recognition on leaderboards"]
        },
        {
            "level": 10,
            "name": "Titan",
            "min_points": 4000,
            "max_points": None,
            "icon": "level10.png",
            "benefits": ["All platform features", "Exclusive Titan badge", "Recognition program participation"]
        }
    ]
    
    return levels


@router.get("/progress/{user_id}", response_model=dict)
async def get_user_progress(
    user_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progression information for a user.
    
    Args:
        user_id: The ID of the user
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: User progression information
    """
    # Check permissions - users can view their own progress, admins can view anyone's
    if current_user.id != user_id and current_user.role not in ["admin", "regional_manager", "franchise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # This is a placeholder - in a real implementation, you would fetch user progress from the database
    
    # For now, we'll simulate user progress data
    user_progress = {
        "user_id": user_id,
        "total_points": 875,
        "current_level": {
            "level": 8,
            "name": "Legend",
            "min_points": 2000,
            "max_points": 2999,
            "icon": "level8.png"
        },
        "next_level": {
            "level": 9,
            "name": "Champion",
            "min_points": 3000,
            "max_points": 3999,
            "icon": "level9.png",
            "points_needed": 125
        },
        "progress_to_next_level": {
            "current": 875,
            "target": 1000,
            "percentage": 87.5
        },
        "activity_stats": {
            "tasks_completed": 42,
            "tasks_completion_rate": 92.5,
            "average_response_time": "6 hours",
            "login_streak": 12,
            "longest_streak": 18
        },
        "trends": {
            "weekly_points": [
                {"week": "Apr 1-7", "points": 120},
                {"week": "Apr 8-14", "points": 150}
            ],
            "monthly_points": [
                {"month": "Jan", "points": 180},
                {"month": "Feb", "points": 210},
                {"month": "Mar", "points": 240},
                {"month": "Apr", "points": 270}
            ]
        }
    }
    
    return user_progress
