"""
Project table definition using SQLModel.

This module defines the SQLModel for the Project entity.
"""

from typing import List

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel
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
    browser_configs: List["BrowserConfig"] = Relationship(cascade_delete=True)
    documents: List["Document"] = Relationship(cascade_delete=True)
    test_cases: List["TestCase"] = Relationship(cascade_delete=True)
    secret_values: List["SecretValue"] = Relationship(cascade_delete=True)
    costs: List["Cost"] = Relationship(cascade_delete=True)
