"""
Education Hub Client Module

This module provides a learning center for clients featuring tutorials, best practices,
industry knowledge, and interactive guides for GMB optimization.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database.session import get_db
from core.auth.dependencies import get_current_user
from apps.client.models.lesson import Lesson
from apps.client.models.progress import Progress


class EducationHub:
    """
    Controller for the Education Hub functionality.
    Manages educational content and client learning progress.
    """
    
    def __init__(self, db: Session):
        """Initialize the education hub controller with database session"""
        self.db = db
        
    def get_available_lessons(
        self, 
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        format_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get available lessons with optional filtering
        
        Args:
            category: Optional category filter
            difficulty: Optional difficulty level filter
            format_type: Optional format type filter
            limit: Number of lessons to return
            offset: Pagination offset
            
        Returns:
            List of lesson data dictionaries
        """
        query = self.db.query(Lesson).filter(Lesson.published == True)
        
        # Apply filters if specified
        if category:
            query = query.filter(Lesson.category == category)
        if difficulty:
            query = query.filter(Lesson.difficulty == difficulty)
        if format_type:
            query = query.filter(Lesson.format == format_type)
            
        # Apply sorting and pagination
        lessons = (
            query
            .order_by(Lesson.category, Lesson.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        # Format results
        return [lesson.to_dict() for lesson in lessons]
    
    def get_lesson_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific lesson by its slug
        
        Args:
            slug: The URL-friendly slug for the lesson
            
        Returns:
            Lesson data dictionary or None if not found
        """
        lesson = self.db.query(Lesson).filter(
            Lesson.slug == slug,
            Lesson.published == True
        ).first()
        
        if not lesson:
            return None
            
        return lesson.to_dict()
    
    def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific lesson by its ID
        
        Args:
            lesson_id: The unique ID of the lesson
            
        Returns:
            Lesson data dictionary or None if not found
        """
        lesson = self.db.query(Lesson).filter(
            Lesson.id == lesson_id,
            Lesson.published == True
        ).first()
        
        if not lesson:
            return None
            
        return lesson.to_dict()
    
    def get_client_progress(self, client_id: str) -> Dict[str, Any]:
        """
        Get the learning progress for a specific client
        
        Args:
            client_id: The client's user ID
            
        Returns:
            Dictionary containing progress statistics and lesson status
        """
        # Get all progress records for the client
        progress_records = (
            self.db.query(Progress)
            .filter(Progress.client_id == client_id)
            .all()
        )
        
        # Calculate overall statistics
        total_lessons = self.db.query(Lesson).filter(Lesson.published == True).count()
        completed_lessons = sum(1 for p in progress_records if p.status == "completed")
        in_progress_lessons = sum(1 for p in progress_records if p.status == "in_progress")
        
        # Format lesson progress records
        lesson_progress = [
            {
                "lesson_id": p.lesson_id,
                "status": p.status,
                "progress_percentage": p.progress_percentage,
                "last_accessed": p.last_accessed.isoformat() if p.last_accessed else None,
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                "bookmarked": p.bookmarked
            }
            for p in progress_records
        ]
        
        # Get lesson details for each progress record
        lessons_with_progress = []
        for progress in lesson_progress:
            lesson = self.db.query(Lesson).filter(Lesson.id == progress["lesson_id"]).first()
            if lesson:
                lesson_data = lesson.to_dict()
                lesson_data["progress"] = progress
                lessons_with_progress.append(lesson_data)
        
        # Calculate completion percentage
        completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return {
            "client_id": client_id,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "in_progress_lessons": in_progress_lessons,
            "not_started_lessons": total_lessons - (completed_lessons + in_progress_lessons),
            "completion_percentage": round(completion_percentage, 1),
            "lessons": lessons_with_progress
        }
    
    def update_lesson_progress(
        self, 
        client_id: str,
        lesson_id: str,
        status: Optional[str] = None,
        progress_percentage: Optional[float] = None,
        bookmarked: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a client's progress on a specific lesson
        
        Args:
            client_id: The client's user ID
            lesson_id: The lesson ID to update progress for
            status: Optional new status ('not_started', 'in_progress', 'completed')
            progress_percentage: Optional new progress percentage (0-100)
            bookmarked: Optional flag to bookmark/unbookmark the lesson
            notes: Optional notes about the lesson
            
        Returns:
            Updated progress data dictionary
        """
        # Verify the lesson exists
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError(f"Lesson with ID {lesson_id} not found")
            
        # Get or create progress record
        progress = (
            self.db.query(Progress)
            .filter(
                Progress.client_id == client_id,
                Progress.lesson_id == lesson_id
            )
            .first()
        )
        
        if not progress:
            # Create new progress record
            progress = Progress(
                id=str(uuid.uuid4()),
                client_id=client_id,
                lesson_id=lesson_id,
                status="not_started",
                progress_percentage=0,
                last_accessed=datetime.utcnow(),
                bookmarked=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(progress)
        
        # Update fields if provided
        if status is not None:
            # Validate status
            valid_statuses = ["not_started", "in_progress", "completed"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
            progress.status = status
            
            # If status is completed, set progress to 100% and completed_at timestamp
            if status == "completed" and progress.status != "completed":
                progress.progress_percentage = 100
                progress.completed_at = datetime.utcnow()
                
        if progress_percentage is not None:
            # Validate percentage
            if not (0 <= progress_percentage <= 100):
                raise ValueError("Progress percentage must be between 0 and 100")
                
            progress.progress_percentage = progress_percentage
            
            # Update status based on progress if not explicitly set
            if status is None:
                if progress_percentage == 0:
                    progress.status = "not_started"
                elif progress_percentage == 100:
                    progress.status = "completed"
                    # Set completed_at if not already set
                    if not progress.completed_at:
                        progress.completed_at = datetime.utcnow()
                else:
                    progress.status = "in_progress"
        
        if bookmarked is not None:
            progress.bookmarked = bookmarked
            
        if notes is not None:
            progress.notes = notes
            
        # Update timestamps
        progress.last_accessed = datetime.utcnow()
        progress.updated_at = datetime.utcnow()
        
        # Commit changes
        self.db.commit()
        self.db.refresh(progress)
        
        return progress.to_dict()
    
    def get_recommended_lessons(self, client_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized lesson recommendations for a client
        
        Args:
            client_id: The client's user ID
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended lesson dictionaries
        """
        # Get client's progress
        progress_records = (
            self.db.query(Progress)
            .filter(Progress.client_id == client_id)
            .all()
        )
        
        # Get lessons the client has already completed
        completed_lesson_ids = [
            p.lesson_id for p in progress_records 
            if p.status == "completed"
        ]
        
        # Get lessons the client has started but not completed
        in_progress_lesson_ids = [
            p.lesson_id for p in progress_records 
            if p.status == "in_progress"
        ]
        
        # First, prioritize in-progress lessons
        if in_progress_lesson_ids:
            in_progress_lessons = (
                self.db.query(Lesson)
                .filter(
                    Lesson.id.in_(in_progress_lesson_ids),
                    Lesson.published == True
                )
                .limit(limit)
                .all()
            )
            
            if in_progress_lessons:
                return [lesson.to_dict() for lesson in in_progress_lessons]
        
        # Then, recommend new lessons based on completed lessons
        # For simplicity, this just recommends beginner lessons the client hasn't started yet
        # A more sophisticated implementation would use actual recommendation algorithms
        recommended_lessons = (
            self.db.query(Lesson)
            .filter(
                Lesson.published == True,
                ~Lesson.id.in_(completed_lesson_ids + in_progress_lesson_ids),
                Lesson.difficulty == "beginner"
            )
            .order_by(Lesson.created_at.desc())
            .limit(limit)
            .all()
        )
        
        # If not enough beginner lessons, add intermediate lessons
        if len(recommended_lessons) < limit:
            additional_lessons = (
                self.db.query(Lesson)
                .filter(
                    Lesson.published == True,
                    ~Lesson.id.in_(completed_lesson_ids + in_progress_lesson_ids),
                    Lesson.difficulty == "intermediate"
                )
                .order_by(Lesson.created_at.desc())
                .limit(limit - len(recommended_lessons))
                .all()
            )
            
            recommended_lessons.extend(additional_lessons)
            
        return [lesson.to_dict() for lesson in recommended_lessons]
        
    def get_lesson_categories(self) -> List[Dict[str, Any]]:
        """
        Get all lesson categories with counts
        
        Returns:
            List of category dictionaries with counts
        """
        # Query distinct categories and count lessons in each
        categories = (
            self.db.query(
                Lesson.category, 
                self.db.func.count(Lesson.id).label("count")
            )
            .filter(Lesson.published == True)
            .group_by(Lesson.category)
            .all()
        )
        
        # Format results
        return [
            {
                "name": category,
                "count": count
            }
            for category, count in categories
        ]


# Factory function to create a controller
def get_education_hub_controller(db: Session = Depends(get_db)):
    """Factory function to create an EducationHub instance"""
    return EducationHub(db)
