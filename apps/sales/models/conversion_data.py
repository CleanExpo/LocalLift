"""
ConversionData model for sales funnel analytics

Generated on 2025-04-15 00:50:56
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from core.database.base import Base


class DateRangeType(enum.Enum):
    """Enum for date range types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ConversionData(Base):
    """
    ConversionData model for tracking sales funnel metrics and conversion rates
    """
    __tablename__ = "conversion_data"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team_id = Column(String, ForeignKey("teams.id"), index=True)
    date_range = Column(String, nullable=False)  # One of: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    lead_count = Column(Integer, default=0)
    qualified_count = Column(Integer, default=0)
    proposal_count = Column(Integer, default=0)
    closed_count = Column(Integer, default=0)
    conversion_rates = Column(JSON, default=dict)
    average_sale_value = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    funnel_stages = relationship("SalesFunnelStage", back_populates="conversion_data", cascade="all, delete-orphan")
    team = relationship("Team", back_populates="conversion_data")

    def __repr__(self):
        return f"<ConversionData(id={self.id}, team_id={self.team_id}, date_range={self.date_range})>"

    def to_dict(self):
        """
        Convert the model to a dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "team_id": self.team_id,
            "date_range": self.date_range,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "lead_count": self.lead_count,
            "qualified_count": self.qualified_count,
            "proposal_count": self.proposal_count,
            "closed_count": self.closed_count,
            "conversion_rates": self.conversion_rates,
            "average_sale_value": self.average_sale_value,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "funnel_stages": [stage.to_dict() for stage in self.funnel_stages] if self.funnel_stages else []
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversionData":
        """
        Create a model instance from a dictionary

        Args:
            data (Dict[str, Any]): Dictionary with model data

        Returns:
            ConversionData: Model instance
        """
        # Remove nested funnel_stages if present
        funnel_stages = data.pop("funnel_stages", None)
        instance = cls(**data)
        return instance

    def calculate_conversion_rates(self):
        """
        Calculate conversion rates for each stage of the funnel
        
        Returns:
            Dict[str, float]: Dictionary of conversion rates
        """
        rates = {}
        
        # Lead to Qualified rate
        if self.lead_count > 0:
            rates["lead_to_qualified"] = (self.qualified_count / self.lead_count) * 100
        else:
            rates["lead_to_qualified"] = 0
            
        # Qualified to Proposal rate
        if self.qualified_count > 0:
            rates["qualified_to_proposal"] = (self.proposal_count / self.qualified_count) * 100
        else:
            rates["qualified_to_proposal"] = 0
            
        # Proposal to Closed rate
        if self.proposal_count > 0:
            rates["proposal_to_closed"] = (self.closed_count / self.proposal_count) * 100
        else:
            rates["proposal_to_closed"] = 0
            
        # Overall Lead to Closed rate
        if self.lead_count > 0:
            rates["lead_to_closed"] = (self.closed_count / self.lead_count) * 100
        else:
            rates["lead_to_closed"] = 0
            
        self.conversion_rates = rates
        return rates
