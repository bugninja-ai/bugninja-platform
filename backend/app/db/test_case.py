"""
TestCase table definition using SQLModel.

This module defines the SQLModel for the TestCase entity.
"""

from typing import List, Optional

from cuid2 import Cuid as CUID
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel
from app.db.document import Document
from app.db.test_run import TestRun
from app.db.test_traversal import TestTraversal


class TestCase(TimestampedModel, table=True):
    """
    TestCase table.

    Test cases define specific testing scenarios with configuration details
    including test goals, rules, and domain restrictions. Each test case
    belongs to a project and is associated with a document.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    project_id: str = Field(
        max_length=255, nullable=False, foreign_key="project.id", ondelete="CASCADE"
    )
    document_id: Optional[str] = Field(
        default=None, max_length=255, foreign_key="document.id", ondelete="SET NULL"
    )

    test_name: str = Field(max_length=255, nullable=False)
    test_description: str = Field(nullable=False)
    test_goal: str = Field(nullable=False)
    extra_rules: str = Field(nullable=False)
    url_route: str = Field(max_length=500, nullable=False)
    allowed_domains: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))

    # Relationships
    document: "Document" = Relationship()
    test_traversals: List["TestTraversal"] = Relationship(cascade_delete=True)
