"""
SQLModel-based database models.

This package provides SQLModel-based table definitions that are equivalent
to the existing SQLAlchemy models but use SQLModel for better integration
with FastAPI and Pydantic.
"""

from app.db.brain_state import BrainState
from app.db.action import Action
from app.db.browser_config import BrowserConfig
from app.db.cost import Cost
from app.db.document import Document
from app.db.history_element import HistoryElement
from app.db.project import Project
from app.db.secret_value import SecretValue
from app.db.secret_value_test_case import SecretValueTestCase
from app.db.test_case import TestCase
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_run import TestRun
from app.db.test_traversal import TestTraversal
from sqlmodel import SQLModel

__all__ = [
    "BrainState",
    "Action",
    "BrowserConfig",
    "Cost",
    "Document",
    "HistoryElement",
    "Project",
    "SecretValue",
    "SecretValueTestCase",
    "TestCase",
    "TestCaseBrowserConfig",
    "TestRun",
    "TestTraversal",
]
