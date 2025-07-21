"""
Document table definition using SQLModel.

This module defines the SQLModel for the Document entity.
"""

from cuid2 import Cuid as CUID
from sqlmodel import Field

from app.db.base import TimestampedModel


class Document(TimestampedModel, table=True):
    """
    Document table.

    Documents can be standalone or associated with a specific test case.
    Each document belongs to a project and contains name and content fields.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    project_id: str = Field(
        max_length=255, nullable=False, foreign_key="project.id", ondelete="CASCADE"
    )

    name: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)
