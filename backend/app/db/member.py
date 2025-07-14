"""
Member table definition.

This module defines the SQLAlchemy model for the Member entity.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.organization import Organization


class Member(Base):
    """
    Member table.

    Members represent users who have access to organizations and their projects.
    Each member is associated with a user account and can have different roles
    within the organization.
    """

    __tablename__ = "members"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
