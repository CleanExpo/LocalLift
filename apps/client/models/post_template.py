"""
PostTemplate model for GMB post templates

Generated on 2025-04-15 00:31:00
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class PostTemplate(Base):
    """
    PostTemplate model for reusable Google My Business post templates
    """
    __tablename__ = "post_template"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    name = Column(String, nullable=False)
    content_template = Column(String, nullable=False)
    category = Column(String, index=True)
    tags = Column(JSON, default=list)
    created_by = Column(String, ForeignKey("users.id"), index=True)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    creator = relationship("User", back_populates="post_templates")

    def __repr__(self):
        return f"<PostTemplate(id={self.id}, name={self.name})>"

    def to_dict(self):
        """
        Convert the model to a dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "name": self.name,
            "content_template": self.content_template,
            "category": self.category,
            "tags": self.tags,
            "created_by": self.created_by,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostTemplate":
        """
        Create a model instance from a dictionary

        Args:
            data (Dict[str, Any]): Dictionary with model data

        Returns:
            PostTemplate: Model instance
        """
        return cls(**data)
