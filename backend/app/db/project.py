"""
Project table definition using SQLModel.

This module defines the SQLModel for the Project entity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel

if TYPE_CHECKING:
    from app.db.browser_config import BrowserConfig
    from app.db.cost import Cost
    from app.db.document import Document
    from app.db.secret_value import SecretValue
    from app.db.test_case import TestCase


class Project(TimestampedModel, table=True):
    """
    Project table.

    Projects represent specific testing initiatives.
    Each project can contain multiple test cases, documents, and other testing resources.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    name: str = Field(max_length=255, nullable=False)
    default_start_url: str = Field(
        max_length=500,
        nullable=False,
    )

    # Relationships
    browser_configs: List["BrowserConfig"] = Relationship(
        back_populates="project", cascade_delete=True
    )
    documents: List["Document"] = Relationship(back_populates="project", cascade_delete=True)
    test_cases: List["TestCase"] = Relationship(back_populates="project", cascade_delete=True)
    secret_values: List["SecretValue"] = Relationship(back_populates="project", cascade_delete=True)
    costs: List["Cost"] = Relationship(back_populates="project", cascade_delete=True)
