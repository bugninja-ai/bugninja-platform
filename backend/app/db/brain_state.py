"""
BrainState table definition.

This module defines the SQLAlchemy model for the BrainState entity.
"""

from typing import List

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.action import Action
from app.db.base import DBTableBaseModel
from app.db.test_run import TestRun


class BrainState(DBTableBaseModel):
    """
    BrainState table.

    Brain states represent the AI agent's cognitive state during test execution.
    Each brain state contains the agent's current understanding, memory,
    and next goals for the test run.
    """

    __tablename__ = "brain_states"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    test_run_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Brain state information
    idx_in_run: Mapped[int] = mapped_column(Integer, nullable=False)
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluation_previous_goal: Mapped[str] = mapped_column(Text, nullable=False)
    memory: Mapped[str] = mapped_column(Text, nullable=False)
    next_goal: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="brain_states")
    actions: Mapped[List["Action"]] = relationship("Action", back_populates="brain_state")
