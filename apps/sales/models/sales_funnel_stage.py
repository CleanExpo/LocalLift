"""
SalesFunnelStage model for sales funnel analysis

Generated on 2025-04-15 00:50:56
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class SalesFunnelStage(Base):
    """
    SalesFunnelStage model for tracking individual stages in a sales funnel
    """
    __tablename__ = "sales_funnel_stage"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversion_data_id = Column(String, ForeignKey("conversion_data.id"), index=True)
    stage_name = Column(String, nullable=False)
    entry_count = Column(Integer, default=0)
    exit_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    average_time_in_stage = Column(Float, default=0.0)  # In days

    # Relationships
    conversion_data = relationship("ConversionData", back_populates="funnel_stages")

    def __repr__(self):
        return f"<SalesFunnelStage(id={self.id}, stage={self.stage_name})>"

    def to_dict(self):
        """
        Convert the model to a dictionary

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            "id": self.id,
            "conversion_data_id": self.conversion_data_id,
            "stage_name": self.stage_name,
            "entry_count": self.entry_count,
            "exit_count": self.exit_count,
            "conversion_rate": self.conversion_rate,
            "average_time_in_stage": self.average_time_in_stage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalesFunnelStage":
        """
        Create a model instance from a dictionary

        Args:
            data (Dict[str, Any]): Dictionary with model data

        Returns:
            SalesFunnelStage: Model instance
        """
        return cls(**data)
    
    def calculate_conversion_rate(self):
        """
        Calculate the conversion rate for this stage
        
        Returns:
            float: Conversion rate as a percentage
        """
        if self.entry_count > 0:
            self.conversion_rate = (self.exit_count / self.entry_count) * 100
        else:
            self.conversion_rate = 0
        return self.conversion_rate
    
    @classmethod
    def create_standard_stages(cls, conversion_data_id: str) -> List["SalesFunnelStage"]:
        """
        Create standard sales funnel stages
        
        Args:
            conversion_data_id: ID of the conversion data record
            
        Returns:
            List[SalesFunnelStage]: List of standard funnel stages
        """
        from uuid import uuid4
        
        stages = [
            cls(
                id=str(uuid4()),
                conversion_data_id=conversion_data_id,
                stage_name="Lead Generation",
                entry_count=0,
                exit_count=0,
                conversion_rate=0,
                average_time_in_stage=0
            ),
            cls(
                id=str(uuid4()),
                conversion_data_id=conversion_data_id,
                stage_name="Qualification",
                entry_count=0,
                exit_count=0,
                conversion_rate=0,
                average_time_in_stage=0
            ),
            cls(
                id=str(uuid4()),
                conversion_data_id=conversion_data_id,
                stage_name="Proposal",
                entry_count=0,
                exit_count=0,
                conversion_rate=0,
                average_time_in_stage=0
            ),
            cls(
                id=str(uuid4()),
                conversion_data_id=conversion_data_id,
                stage_name="Negotiation",
                entry_count=0,
                exit_count=0,
                conversion_rate=0,
                average_time_in_stage=0
            ),
            cls(
                id=str(uuid4()),
                conversion_data_id=conversion_data_id,
                stage_name="Closing",
                entry_count=0,
                exit_count=0,
                conversion_rate=0,
                average_time_in_stage=0
            )
        ]
        
        return stages
