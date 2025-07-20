"""
BrowserConfig table definition using SQLModel.

This module defines the SQLModel for the BrowserConfig entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from cuid2 import Cuid as CUID
from sqlmodel import JSON, Column, Field, Relationship

from app.db.base import TimestampedModel
from app.db.test_case_browser_config import TestCaseBrowserConfig

if TYPE_CHECKING:
    from app.db.project import Project
    from app.db.test_case import TestCase
    from app.db.test_run import TestRun
    from app.db.test_traversal import TestTraversal


class BrowserConfig(TimestampedModel, table=True):
    """
    BrowserConfig table.

    Browser configurations store browser-specific settings and parameters
    that can be used during test execution. These configurations are
    reusable across different test cases.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    project_id: str = Field(
        max_length=255, nullable=False, foreign_key="project.id", ondelete="CASCADE"
    )

    browser_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # Relationships
    project: "Project" = Relationship(back_populates="browser_configs")
    test_runs: List["TestRun"] = Relationship(back_populates="browser_config")
    test_traversals: List["TestTraversal"] = Relationship(
        back_populates="browser_config", cascade_delete=True
    )
    test_cases: List["TestCase"] = Relationship(
        back_populates="browser_configs", link_model=TestCaseBrowserConfig
    )
