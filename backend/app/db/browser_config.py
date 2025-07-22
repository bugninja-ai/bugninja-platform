"""
BrowserConfig table definition using SQLModel.

This module defines the SQLModel for the BrowserConfig entity.
"""

from typing import Any, Dict

from cuid2 import Cuid as CUID
from sqlmodel import JSON, Column, Field

from app.db.base import TimestampedModel


class BrowserConfig(TimestampedModel, table=True):
    """
    BrowserConfig table.

    Browser configurations store browser-specific settings and parameters
    that can be used during test execution. These configurations are
    reusable across different test cases.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    project_id: str = Field(
        max_length=255, nullable=False, foreign_key="project.id", ondelete="CASCADE"
    )

    browser_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
