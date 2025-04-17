"""
RegionStats model for regional performance tracking

Generated on 2025-04-15 00:50:44
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class RegionStats(Base):
    """
    RegionStats model for tracking performance metrics by geographic region
    """
    __tablename__ = "region_stats"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    region_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_province = Column(String, nullable=False)
    city = Column(String, nullable=True)
    total_clients = Column(Integer, default=0)
    active_clients = Column(Integer, default=0)
    average_engagement = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    year_over_year_growth = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    leaderboard_entries = relationship("LeaderboardEntry", back_populates="region")

    def __repr__(self):
        return f"<RegionStats(id={self.id}, name={self.name})>"

    def to_dict(self):
        """
        Convert the model to a dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "region_id": self.region_id,
            "name": self.name,
            "country": self.country,
            "state_province": self.state_province,
            "city": self.city,
            "total_clients": self.total_clients,
            "active_clients": self.active_clients,
            "average_engagement": self.average_engagement,
            "total_revenue": self.total_revenue,
            "year_over_year_growth": self.year_over_year_growth,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegionStats":
        """
        Create a model instance from a dictionary

        Args:
            data (Dict[str, Any]): Dictionary with model data

        Returns:
            RegionStats: Model instance
        """
        return cls(**data)
