"""
Cost table definition using SQLModel.

This module defines the SQLModel for the Cost entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel

if TYPE_CHECKING:
    from app.db.project import Project
    from app.db.test_run import TestRun


class Cost(TimestampedModel, table=True):
    """
    Cost table.

    Cost records track AI model usage costs and token consumption for test runs.
    Each cost record is associated with a specific test run and project,
    tracking the financial impact of AI-powered testing.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    test_run_id: Optional[str] = Field(default=None, max_length=255, foreign_key="testrun.id")
    project_id: str = Field(
        max_length=255, nullable=False, foreign_key="project.id", ondelete="CASCADE"
    )

    model_type: str = Field(max_length=255, nullable=False)
    cost_per_token: float = Field(nullable=False)
    input_token_num: int = Field(nullable=False)
    completion_token_num: int = Field(nullable=False)
    cost_in_dollars: float = Field(nullable=False)

    # Relationships
    test_run: "TestRun" = Relationship(back_populates="cost")
    project: "Project" = Relationship(back_populates="costs")
