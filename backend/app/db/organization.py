"""
Organization table definition.

This module defines the SQLAlchemy model for the Organization entity.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.member import Member
from app.db.project import Project


class Organization(Base):
    """
    Organization table.

    Organizations represent companies or teams that can contain multiple projects.
    Each organization can have multiple members and projects associated with it.
    """

    __tablename__ = "organizations"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo: Mapped[str] = mapped_column(String(500), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="organization")
    members: Mapped[List["Member"]] = relationship("Member", back_populates="organization")
