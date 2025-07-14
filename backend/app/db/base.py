"""
Database base and model exports.

This module provides the base class and exports all database models.
"""

from sqlalchemy.orm import DeclarativeBase

# Import all models to ensure they are registered
from app.db.action import Action
from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.cost import Cost
from app.db.document import Document
from app.db.history_element import HistoryElement
from app.db.member import Member
from app.db.organization import Organization
from app.db.project import Project
from app.db.secret_value import SecretValue
from app.db.secret_value_test_traversal import SecretValueTestTraversal
from app.db.test_case import TestCase
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_run import TestRun
from app.db.test_traversal import TestTraversal


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


__all__ = [
    "Base",
    "Action",
    "BrainState",
    "BrowserConfig",
    "Cost",
    "Document",
    "HistoryElement",
    "Member",
    "Organization",
    "Project",
    "SecretValue",
    "SecretValueTestTraversal",
    "TestCase",
    "TestCaseBrowserConfig",
    "TestRun",
    "TestTraversal",
]
