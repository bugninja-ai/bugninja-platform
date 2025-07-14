"""
TestRun table definition.

This module defines the SQLAlchemy model for the TestRun entity.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.browser_config import BrowserConfig
from app.db.cost import Cost
from app.db.history_element import HistoryElement
from app.db.test_traversal import TestTraversal


class TestRun(Base):
    """
    TestRun table.

    Test runs represent actual executions of test traversals with detailed tracking
    of the execution process, timing, and outcomes. Each test run can have different
    types and origins, and tracks the complete execution history.
    """

    __tablename__ = "test_runs"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    test_traversal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    browser_config_id: Mapped[str] = mapped_column(String(255), nullable=False)
    cost_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Run information
    run_type: Mapped[str] = mapped_column(
        Enum("AGENTIC", "REPLAY", "REPLAY_WITH_HEALING", name="run_type"), nullable=False
    )
    origin: Mapped[str] = mapped_column(Enum("USER", "CICD", name="run_origin"), nullable=False)
    repair_was_needed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    current_state: Mapped[str] = mapped_column(
        Enum("STARTING", "RUNNING", "FINISHED", name="run_state"), nullable=False
    )
    run_gif: Mapped[str] = mapped_column(String(500), nullable=False)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    test_traversal: Mapped["TestTraversal"] = relationship(
        "TestTraversal", back_populates="test_runs"
    )
    browser_config: Mapped["BrowserConfig"] = relationship(
        "BrowserConfig", back_populates="test_runs"
    )
    cost: Mapped[Optional["Cost"]] = relationship("Cost", back_populates="test_run")
    history_elements: Mapped[List["HistoryElement"]] = relationship(
        "HistoryElement", back_populates="test_run"
    )
