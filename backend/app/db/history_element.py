"""
HistoryElement table definition using SQLModel.

This module defines the SQLModel for the HistoryElement entity.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from cuid2 import Cuid as CUID
from sqlmodel import Column
from sqlmodel import Enum as SQLModelEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.action import Action
    from app.db.test_run import TestRun


class HistoryElementState(str, enum.Enum):
    """Enumeration for history element states."""

    PASSED = "PASSED"
    FAILED = "FAILED"


class HistoryElement(SQLModel, table=True):
    """
    HistoryElement table.

    History elements track individual actions and their outcomes during test execution.
    Each history element represents a single action taken by the AI agent during
    a test run, including timing, results, and visual evidence.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)

    test_run_id: str = Field(
        max_length=255, nullable=False, foreign_key="testrun.id", ondelete="CASCADE"
    )
    action_id: str = Field(
        max_length=255, nullable=False, foreign_key="action.id", ondelete="CASCADE"
    )

    action_started_at: datetime = Field(nullable=False)
    action_finished_at: datetime = Field(nullable=False)

    history_element_state: HistoryElementState = Field(
        default=HistoryElementState.PASSED,
        sa_column=Column(SQLModelEnum(HistoryElementState, name="historyelementstate")),
    )
    screenshot: Optional[str] = Field(default=None)

    # Relationships
    test_run: "TestRun" = Relationship(back_populates="history_elements")
    action: "Action" = Relationship(back_populates="history_elements")
