"""
Base models for all entities.
Uses SQLAlchemy with async support.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.orm import declarative_mixin

from app.core.database import Base


@declarative_mixin
class BaseModel:
    """
    Base model with common fields.
    All models should inherit from this.
    """

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
