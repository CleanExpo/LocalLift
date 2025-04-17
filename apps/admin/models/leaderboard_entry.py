"""
LeaderboardEntry model for regional performance leaderboard

Generated on 2025-04-15 00:50:44
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON, Enum
import enum
from sqlalchemy.orm import relationship
from core.database.base import Base


class TrendDirection(enum.Enum):
    """Enum for trend direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class MetricType(enum.Enum):
    """Enum for metric types"""
    REVENUE = "revenue"
    GROWTH = "growth"
    ENGAGEMENT = "engagement"
    COMPLIANCE = "compliance"


class LeaderboardEntry(Base):
    """
    LeaderboardEntry model for regional performance rankings
    """
    __tablename__ = "leaderboard_entry"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    region_id = Column(String, ForeignKey("region_stats.region_id"), index=True)
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    metric_type = Column(String, nullable=False)  # One of: 'revenue', 'growth', 'engagement', 'compliance'
    previous_rank = Column(Integer, nullable=True)
    trend = Column(String, nullable=False, default=TrendDirection.STABLE.value)  # One of: 'up', 'down', 'stable'
    
    # Relationships
    region = relationship("RegionStats", back_populates="leaderboard_entries")

    def __repr__(self):
        return f"<LeaderboardEntry(id={self.id}, rank={self.rank}, metric={self.metric_type})>"

    def to_dict(self):
        """
        Convert the model to a dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "region_id": self.region_id,
            "rank": self.rank,
            "score": self.score,
            "metric_type": self.metric_type,
            "previous_rank": self.previous_rank,
            "trend": self.trend,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeaderboardEntry":
        """
        Create a model instance from a dictionary

        Args:
            data (Dict[str, Any]): Dictionary with model data

        Returns:
            LeaderboardEntry: Model instance
        """
        return cls(**data)
    
    def calculate_trend(self):
        """
        Calculate the trend based on current and previous rank
        
        Returns:
            str: Trend direction ('up', 'down', 'stable')
        """
        if self.previous_rank is None:
            return TrendDirection.STABLE.value
            
        if self.rank < self.previous_rank:
            return TrendDirection.UP.value
        elif self.rank > self.previous_rank:
            return TrendDirection.DOWN.value
        else:
            return TrendDirection.STABLE.value
