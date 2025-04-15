"""
EngagementMetric model for description module

Generated on 2025-04-15 01:20:53
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class EngagementMetric(Base):
    """
    EngagementMetric model
    """
    __tablename__ = "engagement_metric"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    id = Column(String)(primary key)
    report_id = Column(String)(foreign key to WeeklyReport.id)
    metric_type = Column(String)('views', 'clicks', 'calls', 'direction_requests', 'messages', 'bookings')
    current_value = Column(Integer)
    previous_value = Column(Integer)
    change_percentage = Column(Float)
    trend = Column(String)('up', 'down', 'stable')
    benchmark_value = Column(Float, nullable=True)
    benchmark_comparison = Column(String, nullable=True)('above', 'below', 'equal')
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<EngagementMetric(id={self.id})>"
    
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
    def from_dict(cls, data: Dict[str, Any]) -> "EngagementMetric":
        """
        Create a model instance from a dictionary
        
        Args:
            data (Dict[str, Any]): Dictionary with model data
            
        Returns:
            EngagementMetric: Model instance
        """
        return cls(**data)
