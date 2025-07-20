"""
TestCase-BrowserConfig association table using SQLModel.

This module defines the association table for the many-to-many relationship
between TestCase and BrowserConfig entities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class TestCaseBrowserConfig(SQLModel, table=True):
    """
    Association table for TestCase and BrowserConfig many-to-many relationship.

    This table connects test cases to browser configurations, allowing multiple
    browser configs to be used with a single test case and multiple test cases
    to use the same browser configurations.
    """

    # Foreign keys (composite primary key)
    test_case_id: str = Field(primary_key=True, max_length=255, foreign_key="testcase.id")
    browser_config_id: str = Field(primary_key=True, max_length=255, foreign_key="browserconfig.id")
