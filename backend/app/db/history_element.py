"""
HistoryElement table definition.

This module defines the SQLAlchemy model for the HistoryElement entity.
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.action import Action
from app.db.base import Base
from app.db.test_run import TestRun


class HistoryElement(Base):
    """
    HistoryElement table.

    History elements track individual actions and their outcomes during test execution.
    Each history element represents a single action taken by the AI agent during
    a test run, including timing, results, and visual evidence.
    """

    __tablename__ = "history_elements"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    test_run_id: Mapped[str] = mapped_column(String(255), nullable=False)
    action_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # History information
    action_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    action_finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    history_element_state: Mapped[str] = mapped_column(
        Enum("PASSED", "FAILED", name="history_element_state"), nullable=False
    )
    screenshot: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relationships
    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="history_elements")
    action: Mapped["Action"] = relationship("Action", back_populates="history_elements")
