"""
Project table definition.

This module defines the SQLAlchemy model for the Project entity.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.cost import Cost
from app.db.document import Document
from app.db.organization import Organization
from app.db.secret_value import SecretValue
from app.db.test_case import TestCase
from app.db.test_traversal import TestTraversal


class Project(Base):
    """
    Project table.

    Projects represent specific testing initiatives within an organization.
    Each project belongs to an organization and can contain multiple test cases,
    documents, and other testing resources.
    """

    __tablename__ = "projects"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_start_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="projects")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project")
    test_cases: Mapped[List["TestCase"]] = relationship("TestCase", back_populates="project")
    secret_values: Mapped[List["SecretValue"]] = relationship(
        "SecretValue", back_populates="project"
    )
    test_traversals: Mapped[List["TestTraversal"]] = relationship(
        "TestTraversal", back_populates="project"
    )
    costs: Mapped[List["Cost"]] = relationship("Cost", back_populates="project")
