"""
TestCase table definition.

This module defines the SQLAlchemy model for the TestCase entity.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import DBTableBaseModel
from app.db.browser_config import BrowserConfig
from app.db.document import Document
from app.db.project import Project
from app.db.test_run import TestRun


class TestCase(DBTableBaseModel):
    """
    TestCase table.

    Test cases define specific testing scenarios with configuration details
    including test goals, rules, and domain restrictions. Each test case
    belongs to a project and is associated with a document.
    """

    __tablename__ = "test_cases"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    project_id: Mapped[str] = mapped_column(String(255), nullable=False)
    document_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Test information
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_description: Mapped[str] = mapped_column(Text, nullable=False)
    test_goal: Mapped[str] = mapped_column(Text, nullable=False)
    extra_rules: Mapped[str] = mapped_column(Text, nullable=False)
    url_route: Mapped[str] = mapped_column(String(500), nullable=False)
    allowed_domains: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="test_cases")
    document: Mapped["Document"] = relationship("Document", back_populates="test_case")
    test_runs: Mapped[List["TestRun"]] = relationship("TestRun", back_populates="test_case")
    browser_configs: Mapped[List["BrowserConfig"]] = relationship(
        "BrowserConfig", secondary="test_case_browser_configs", back_populates="test_cases"
    )
