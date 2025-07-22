"""
Action table definition using SQLModel.

This module defines the SQLModel for the Action entity.
"""

from typing import Any, Dict

from cuid2 import Cuid as CUID
from sqlmodel import JSON, Column, Field

from app.db.base import TimestampedModel


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
