"""
TestRun table definition using SQLModel.

This module defines the SQLModel for the TestRun entity.
"""

import enum
from datetime import datetime
from typing import List, Optional

from cuid2 import Cuid as CUID
from sqlmodel import Column
from sqlmodel import Enum as SQLModelEnum
from sqlmodel import Field, Relationship, SQLModel

from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.cost import Cost
from app.db.history_element import HistoryElement


class RunType(str, enum.Enum):
    """Enumeration for test run types."""

    AGENTIC = "AGENTIC"
    REPLAY = "REPLAY"
    REPLAY_WITH_HEALING = "REPLAY_WITH_HEALING"


class RunOrigin(str, enum.Enum):
    """Enumeration for test run origins."""

    USER = "USER"
    CICD = "CICD"


class RunState(str, enum.Enum):
    """Enumeration for test run states."""

    STARTING = "STARTING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


class TestRun(SQLModel, table=True):
    """
    TestRun table.

    Test runs represent actual executions of test traversals with detailed tracking
    of the execution process, timing, and outcomes. Each test run can have different
    types and origins, and tracks the complete execution history.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    test_traversal_id: str = Field(
        max_length=255, nullable=False, foreign_key="testtraversal.id", ondelete="CASCADE"
    )
    browser_config_id: Optional[str] = Field(
        default=None, max_length=255, foreign_key="browserconfig.id", ondelete="SET NULL"
    )

    run_type: RunType = Field(
        default=RunType.AGENTIC,
        sa_column=Column(SQLModelEnum(RunType, name="runtype")),
    )
    origin: RunOrigin = Field(
        default=RunOrigin.USER,
        sa_column=Column(SQLModelEnum(RunOrigin, name="runorigin")),
    )
    repair_was_needed: bool = Field(nullable=False)
    current_state: RunState = Field(
        default=RunState.STARTING,
        sa_column=Column(SQLModelEnum(RunState, name="runstate")),
    )
    run_gif: str = Field(max_length=500, nullable=False)
    started_at: datetime = Field(nullable=False)
    finished_at: datetime = Field(nullable=False)

    # Relationships
    browser_config: "BrowserConfig" = Relationship()
    history_elements: List["HistoryElement"] = Relationship(cascade_delete=True)
    cost: "Cost" = Relationship()
