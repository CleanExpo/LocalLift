"""
ClientFilter model for description module

Generated on 2025-04-14 23:54:45
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database.base import Base


class ClientFilter(Base):
    """
    ClientFilter model
    """
    __tablename__ = "client_filter"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    name = Column(String)
    created_by = Column(String)(foreign key to users.id)
    criteria = Column(JSON)
    is_public = Column(Boolean)
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<ClientFilter(id={self.id})>"
    
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
    def from_dict(cls, data: Dict[str, Any]) -> "ClientFilter":
        """
        Create a model instance from a dictionary
        
        Args:
            data (Dict[str, Any]): Dictionary with model data
            
        Returns:
            ClientFilter: Model instance
        """
        return cls(**data)
