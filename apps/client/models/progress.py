"""
Progress Model

This module defines the Progress model for tracking client progress in educational content.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from core.database.base import Base


class Progress(Base):
    """
    Model for tracking client progress through educational content.
    
    Each Progress record represents a client's progress and status for a specific lesson,
    including tracking of completion status, bookmarks, and personal notes.
    """
    __tablename__ = "learning_progress"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    client_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    lesson_id = Column(String, ForeignKey("lessons.id"), index=True, nullable=False)
    
    # Progress tracking
    status = Column(String, nullable=False, default="not_started")  # 'not_started', 'in_progress', 'completed'
    progress_percentage = Column(Float, nullable=False, default=0.0)
    
    # Access and completion timestamps
    last_accessed = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Personal data
    notes = Column(Text, nullable=True)
    bookmarked = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    
    # Additional tracking data
    time_spent_seconds = Column(Integer, default=0)
    custom_data = Column(MutableDict.as_mutable(JSON), default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Use backref to establish relationships with User and Lesson models
    client = relationship("User", backref="learning_progress")
    lesson = relationship("Lesson", backref="progress_records")
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<Progress(id={self.id}, client_id={self.client_id}, lesson_id={self.lesson_id}, status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary for API responses
        
        Returns:
            Dictionary representation of the model
        """
        return {
            "id": self.id,
            "client_id": self.client_id,
            "lesson_id": self.lesson_id,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "bookmarked": self.bookmarked,
            "rating": self.rating,
            "time_spent_seconds": self.time_spent_seconds,
            "custom_data": self.custom_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Progress":
        """
        Create a model instance from a dictionary
        
        Args:
            data: Dictionary with model data
            
        Returns:
            Progress instance
        """
        # Convert ISO format strings to datetime objects
        for date_field in ["last_accessed", "completed_at", "created_at", "updated_at"]:
            if date_field in data and data[date_field] and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        return cls(**data)
    
    def mark_completed(self) -> None:
        """Mark this lesson as completed for the client"""
        self.status = "completed"
        self.progress_percentage = 100.0
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, percentage: float) -> None:
        """
        Update the progress percentage for this lesson
        
        Args:
            percentage: New progress percentage (0-100)
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")
            
        self.progress_percentage = percentage
        
        # Update status based on percentage
        if percentage == 0:
            self.status = "not_started"
        elif percentage == 100:
            self.status = "completed"
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
        else:
            self.status = "in_progress"
            
        self.last_accessed = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def toggle_bookmark(self) -> bool:
        """
        Toggle the bookmark status for this lesson
        
        Returns:
            New bookmark status
        """
        self.bookmarked = not self.bookmarked
        self.updated_at = datetime.utcnow()
        return self.bookmarked
    
    def add_time_spent(self, seconds: int) -> None:
        """
        Add time spent to the lesson tracking
        
        Args:
            seconds: Number of seconds spent on the lesson
        """
        if seconds < 0:
            raise ValueError("Time spent cannot be negative")
            
        self.time_spent_seconds += seconds
        self.last_accessed = datetime.utcnow()
        self.updated_at = datetime.utcnow()
