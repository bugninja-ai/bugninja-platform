"""
BrainState table definition using SQLModel.

This module defines the SQLModel for the BrainState entity.
"""

from typing import List

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.action import Action
from app.db.base import TimestampedModel


class BrainState(TimestampedModel, table=True):
    """
    BrainState table.

    Brain states represent the AI agent's cognitive state during test execution.
    Each brain state contains the agent's current understanding, memory,
    and next goals for the test run.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    test_traversal_id: str = Field(
        max_length=255, nullable=False, foreign_key="testtraversal.id", ondelete="CASCADE"
    )

    idx_in_run: int = Field(nullable=False)
    valid: bool = Field(nullable=False)
    evaluation_previous_goal: str = Field(nullable=False)
    memory: str = Field(nullable=False)
    next_goal: str = Field(nullable=False)

    # Relationships
    actions: List[Action] = Relationship(cascade_delete=True)
