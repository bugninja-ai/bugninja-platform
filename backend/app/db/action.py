"""
Action table definition using SQLModel.

This module defines the SQLModel for the Action entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from cuid2 import Cuid as CUID
from sqlmodel import JSON, Column, Field, Relationship

from app.db.base import TimestampedModel

if TYPE_CHECKING:
    from app.db.brain_state import BrainState
    from app.db.history_element import HistoryElement


class Action(TimestampedModel, table=True):
    """
    Action table.

    Actions represent specific UI interactions performed by the AI agent during test execution.
    Each action is associated with a brain state and contains details about the interaction
    including the action type and DOM element data.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    brain_state_id: str = Field(
        max_length=255, nullable=False, foreign_key="brainstate.id", ondelete="CASCADE"
    )

    idx_in_brain_state: int = Field(nullable=False)
    action: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    dom_element_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    valid: bool = Field(nullable=False)

    # Relationships
    brain_state: "BrainState" = Relationship(back_populates="actions")
    history_elements: List["HistoryElement"] = Relationship(
        back_populates="action", cascade_delete=True
    )
