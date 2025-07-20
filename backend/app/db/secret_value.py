"""
SecretValue table definition using SQLModel.

This module defines the SQLModel for the SecretValue entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel
from app.db.secret_value_test_traversal import SecretValueTestTraversal

if TYPE_CHECKING:
    from app.db.project import Project
    from app.db.test_traversal import TestTraversal


class SecretValue(TimestampedModel, table=True):
    """
    SecretValue table.

    Secret values store sensitive configuration data for projects such as
    API keys, passwords, and other credentials. Each secret belongs to
    a specific project and should be encrypted at rest.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    project_id: str = Field(
        max_length=255, nullable=False, foreign_key="project.id", ondelete="CASCADE"
    )

    secret_name: str = Field(max_length=255, nullable=False)
    secret_value: str = Field(nullable=False)  # Should be encrypted

    # Relationships
    project: "Project" = Relationship(back_populates="secret_values")
    test_traversals: List["TestTraversal"] = Relationship(
        back_populates="secret_values", link_model=SecretValueTestTraversal
    )
