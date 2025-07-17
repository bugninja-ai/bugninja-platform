"""
BrowserConfig table definition.

This module defines the SQLAlchemy model for the BrowserConfig entity.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import DBTableBaseModel
from app.db.test_case import TestCase
from app.db.test_run import TestRun


class BrowserConfig(DBTableBaseModel):
    """
    BrowserConfig table.

    Browser configurations store browser-specific settings and parameters
    that can be used during test execution. These configurations are
    reusable across different test cases.
    """

    __tablename__ = "browser_configs"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Configuration data (JSON string)
    browser_config: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    test_runs: Mapped[List["TestRun"]] = relationship("TestRun", back_populates="browser_config")
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase", secondary="test_case_browser_configs", back_populates="browser_configs"
    )
