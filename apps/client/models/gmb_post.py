"""
GmbPost model for GMB post tracking

Generated on 2025-04-15 00:31:00
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class GmbPost(Base):
    """
    GmbPost model for tracking Google My Business posts
    """
    __tablename__ = "gmb_post"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client_id = Column(String, ForeignKey("users.id"), index=True)
    post_id = Column(String, unique=True)
    content = Column(String)
    image_url = Column(String, nullable=True)
    scheduled_date = Column(DateTime)
    published_date = Column(DateTime, nullable=True)
    status = Column(String)  # Values: 'draft', 'scheduled', 'published', 'failed'
    metrics = Column(JSON)
    last_updated = Column(DateTime)

    # Relationships
    client = relationship("User", back_populates="gmb_posts")

    def __repr__(self):
        return f"<GmbPost(id={self.id}, status={self.status})>"

    def to_dict(self):
        """
        Convert the model to a dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "client_id": self.client_id,
            "post_id": self.post_id,
            "content": self.content,
            "image_url": self.image_url,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "status": self.status,
            "metrics": self.metrics,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GmbPost":
        """
        Create a model instance from a dictionary

        Args:
            data (Dict[str, Any]): Dictionary with model data

        Returns:
            GmbPost: Model instance
        """
        return cls(**data)
