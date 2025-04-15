"""
Engagement Record Model

This module defines the EngagementRecord model for storing weekly engagement reports
and related metrics for clients.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import relationship

from core.database.base import Base


class EngagementRecord(Base):
    """
    Model for storing weekly engagement reports and metrics for clients.
    
    Each record represents a single weekly report, storing metrics, trends,
    insights, and recommendations for a specific client and time period.
    """
    __tablename__ = "engagement_records"
    
    # Primary key and foreign keys
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    
    # Report metadata
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Report data
    metrics = Column(MutableDict.as_mutable(JSON), default=dict)
    trends = Column(MutableDict.as_mutable(JSON), default=dict)
    insights = Column(MutableList.as_mutable(JSON), default=list)
    recommendations = Column(MutableList.as_mutable(JSON), default=list)
    
    # Status tracking
    viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Use backref to establish relationship with User model
    client = relationship("User", backref="engagement_records")
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<EngagementRecord(id={self.id}, client_id={self.client_id}, week={self.week_number}, year={self.year})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary for API responses
        
        Returns:
            Dictionary representation of the model
        """
        return {
            "id": self.id,
            "client_id": self.client_id,
            "week_number": self.week_number,
            "year": self.year,
            "period": {
                "start_date": self.start_date.isoformat() if self.start_date else None,
                "end_date": self.end_date.isoformat() if self.end_date else None
            },
            "metrics": self.metrics,
            "trends": self.trends,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "viewed": self.viewed,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EngagementRecord":
        """
        Create a model instance from a dictionary
        
        Args:
            data: Dictionary with model data
            
        Returns:
            EngagementRecord instance
        """
        # Extract period if provided
        if "period" in data:
            period = data.pop("period")
            if "start_date" in period:
                data["start_date"] = datetime.fromisoformat(period["start_date"])
            if "end_date" in period:
                data["end_date"] = datetime.fromisoformat(period["end_date"])
        
        # Convert ISO format strings to datetime objects
        for date_field in ["viewed_at", "created_at", "updated_at"]:
            if date_field in data and data[date_field] and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        return cls(**data)
    
    def get_key_metrics(self) -> Dict[str, Any]:
        """
        Get the key metrics for this report
        
        Returns:
            Dictionary with key metrics
        """
        return {
            "views": self.metrics.get("views", 0),
            "clicks": self.metrics.get("clicks", 0),
            "calls": self.metrics.get("calls", 0),
            "messages": self.metrics.get("messages", 0),
            "engagement_rate": self.metrics.get("engagement_rate", 0),
            "conversion_rate": self.metrics.get("conversion_rate", 0)
        }
    
    def get_trend_summary(self) -> Dict[str, str]:
        """
        Get a summary of trends
        
        Returns:
            Dictionary with trend summaries
        """
        trend_summary = {}
        
        for key, value in self.trends.items():
            if isinstance(value, dict) and "direction" in value:
                trend_summary[key] = value["direction"]
        
        return trend_summary
