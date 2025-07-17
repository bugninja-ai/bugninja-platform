"""
TestTraversal table definition.

This module defines the SQLAlchemy model for the TestTraversal entity.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import DBTableBaseModel
from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.project import Project
from app.db.secret_value import SecretValue
from app.db.test_case import TestCase
from app.db.test_run import TestRun


class TestTraversal(DBTableBaseModel):
    """
    TestTraversal table.

    Test traversals represent specific test execution paths that combine
    a test case with a browser configuration. Each traversal belongs to
    a project and defines how a test should be executed.
    """

    __tablename__ = "test_traversals"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    project_id: Mapped[str] = mapped_column(String(255), nullable=False)
    test_case_id: Mapped[str] = mapped_column(String(255), nullable=False)
    browser_config_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Traversal information
    traversal_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="test_traversals")
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="test_traversals")
    browser_config: Mapped["BrowserConfig"] = relationship(
        "BrowserConfig", back_populates="test_traversals"
    )
    brain_states: Mapped[List["BrainState"]] = relationship(
        "BrainState", back_populates="test_traversal"
    )
    test_runs: Mapped[List["TestRun"]] = relationship("TestRun", back_populates="test_traversal")
    secret_values: Mapped[List["SecretValue"]] = relationship(
        "SecretValue", secondary="secret_value_test_traversals", back_populates="test_traversals"
    )
