"""
Document table definition.

This module defines the SQLAlchemy model for the Document entity.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import DBTableBaseModel
from app.db.project import Project
from app.db.test_case import TestCase


class Document(DBTableBaseModel):
    """
    Document table.

    Documents can be standalone or associated with a specific test case.
    Each document belongs to a project and contains name and content fields.
    """

    __tablename__ = "documents"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    project_id: Mapped[str] = mapped_column(String(255), nullable=False)
    test_case_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    test_case: Mapped[Optional["TestCase"]] = relationship("TestCase", back_populates="document")
