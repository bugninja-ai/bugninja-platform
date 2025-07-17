"""
TestCase-BrowserConfig association table.

This module defines the association table for the many-to-many relationship
between TestCase and BrowserConfig entities.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import DBTableBaseModel


class TestCaseBrowserConfig(DBTableBaseModel):
    """
    Association table for TestCase and BrowserConfig many-to-many relationship.

    This table connects test cases to browser configurations, allowing multiple
    browser configs to be used with a single test case and multiple test cases
    to use the same browser configurations.
    """

    __tablename__ = "test_case_browser_configs"

    # Foreign keys
    test_case_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    browser_config_id: Mapped[str] = mapped_column(String(255), primary_key=True)
