"""
Lesson Model

This module defines the Lesson model for storing educational content in the client Education Hub.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import relationship

from core.database.base import Base


class Lesson(Base):
    """
    Model for storing educational content such as tutorials, guides, and articles.
    
    Each lesson represents a single piece of educational content with metadata
    for categorization, difficulty tracking, and content management.
    """
    __tablename__ = "lessons"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic content information
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True)
    
    # Content and formatting
    content = Column(Text, nullable=False)
    format = Column(String, nullable=False)  # 'article', 'video', 'guide', 'checklist'
    difficulty = Column(String, nullable=False)  # 'beginner', 'intermediate', 'advanced'
    
    # Content metadata
    estimated_time = Column(Integer, nullable=False)  # In minutes
    published = Column(Boolean, default=False)
    author_id = Column(String, nullable=True)
    
    # Additional fields
    thumbnail_url = Column(String, nullable=True)
    featured = Column(Boolean, default=False)
    tags = Column(MutableList.as_mutable(JSON), default=list)
    prerequisites = Column(MutableList.as_mutable(JSON), default=list)  # List of lesson IDs
    related_lessons = Column(MutableList.as_mutable(JSON), default=list)  # List of related lesson IDs
    
    # SEO and sharing
    meta_description = Column(String, nullable=True)
    meta_keywords = Column(String, nullable=True)
    
    # Statistics and tracking
    view_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<Lesson(id={self.id}, title='{self.title}', category='{self.category}', difficulty='{self.difficulty}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary for API responses
        
        Returns:
            Dictionary representation of the model
        """
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "category": self.category,
            "subcategory": self.subcategory,
            "content": self.content,
            "format": self.format,
            "difficulty": self.difficulty,
            "estimated_time": self.estimated_time,
            "thumbnail_url": self.thumbnail_url,
            "published": self.published,
            "author_id": self.author_id,
            "featured": self.featured,
            "tags": self.tags,
            "prerequisites": self.prerequisites,
            "related_lessons": self.related_lessons,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "view_count": self.view_count,
            "completion_count": self.completion_count,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lesson":
        """
        Create a model instance from a dictionary
        
        Args:
            data: Dictionary with model data
            
        Returns:
            Lesson instance
        """
        # Convert ISO format strings to datetime objects
        for date_field in ["created_at", "updated_at", "published_at"]:
            if date_field in data and data[date_field] and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        return cls(**data)
    
    def increment_view_count(self) -> None:
        """Increment the view count for this lesson"""
        self.view_count += 1
    
    def increment_completion_count(self) -> None:
        """Increment the completion count for this lesson"""
        self.completion_count += 1
    
    def add_rating(self, rating: float) -> None:
        """
        Add a new rating for this lesson
        
        Args:
            rating: Rating value (1-5)
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Calculate new average
        total_rating = self.average_rating * self.rating_count
        self.rating_count += 1
        self.average_rating = (total_rating + rating) / self.rating_count
