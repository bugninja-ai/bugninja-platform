"""
Action table definition.

This module defines the SQLAlchemy model for the Action entity.
"""

from typing import List

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import DBTableBaseModel
from app.db.brain_state import BrainState
from app.db.history_element import HistoryElement


class Action(DBTableBaseModel):
    """
    Action table.

    Actions represent specific UI interactions performed by the AI agent during test execution.
    Each action is associated with a brain state and contains details about the interaction
    including the action type and DOM element data.
    """

    __tablename__ = "actions"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    brain_state_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Action information
    idx_in_brain_state: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    dom_element_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    brain_state: Mapped["BrainState"] = relationship("BrainState", back_populates="actions")
    history_elements: Mapped[List["HistoryElement"]] = relationship(
        "HistoryElement", back_populates="action"
    )
