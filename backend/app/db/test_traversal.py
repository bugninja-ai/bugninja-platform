"""
TestTraversal table definition using SQLModel.

This module defines the SQLModel for the TestTraversal entity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel
from app.db.secret_value_test_traversal import SecretValueTestTraversal

if TYPE_CHECKING:
    from app.db.brain_state import BrainState
    from app.db.browser_config import BrowserConfig
    from app.db.project import Project
    from app.db.secret_value import SecretValue
    from app.db.test_case import TestCase
    from app.db.test_run import TestRun


class TestTraversal(TimestampedModel, table=True):
    """
    TestTraversal table.

    Test traversals represent specific test execution paths that combine
    a test case with a browser configuration. Each traversal belongs to
    a project and defines how a test should be executed.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    test_case_id: str = Field(
        max_length=255, nullable=False, foreign_key="testcase.id", ondelete="CASCADE"
    )
    browser_config_id: str = Field(
        max_length=255, nullable=False, foreign_key="browserconfig.id", ondelete="CASCADE"
    )

    traversal_name: str = Field(max_length=255, nullable=False)

    # Relationships
    project: "Project" = Relationship(back_populates="test_traversals")
    test_case: "TestCase" = Relationship(back_populates="test_traversals")
    browser_config: "BrowserConfig" = Relationship(back_populates="test_traversals")

    brain_states: List["BrainState"] = Relationship(
        back_populates="test_traversal", cascade_delete=True
    )
    test_runs: List["TestRun"] = Relationship(back_populates="test_traversal", cascade_delete=True)
    secret_values: List["SecretValue"] = Relationship(
        back_populates="test_traversals", link_model=SecretValueTestTraversal
    )
