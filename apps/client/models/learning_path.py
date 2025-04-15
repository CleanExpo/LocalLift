"""
LearningPath model for description module

Generated on 2025-04-15 01:43:56
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class LearningPath(Base):
    """
    LearningPath model
    """
    __tablename__ = "learning_path"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    id = Column(String)(primary key)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    content_ids = Column(JSON)
    required_order = Column(Boolean)
    estimated_completion_days = Column(Integer)
    difficulty = Column(String)('beginner', 'intermediate', 'advanced')
    published = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return f"<LearningPath(id={self.id})>"
    
    def to_dict(self):
        """
        Convert the model to a dictionary
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Add other attributes here
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningPath":
        """
        Create a model instance from a dictionary
        
        Args:
            data (Dict[str, Any]): Dictionary with model data
            
        Returns:
            LearningPath: Model instance
        """
        return cls(**data)
