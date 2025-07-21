"""
TestTraversal table definition using SQLModel.

This module defines the SQLModel for the TestTraversal entity.
"""

from typing import List

from cuid2 import Cuid as CUID
from sqlmodel import Field, Relationship

from app.db.base import TimestampedModel
from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.secret_value import SecretValue
from app.db.secret_value_test_traversal import SecretValueTestTraversal
from app.db.test_run import TestRun


class TestTraversal(TimestampedModel, table=True):
    """
    TestTraversal table.

    Test traversals represent specific test execution paths that combine
    a test case with a browser configuration. Each traversal belongs to
    a project and defines how a test should be executed.
    """

    # Primary key
    id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)
    test_case_id: str = Field(
        max_length=255, nullable=False, foreign_key="testcase.id", ondelete="CASCADE"
    )
    browser_config_id: str = Field(
        max_length=255, nullable=False, foreign_key="browserconfig.id", ondelete="CASCADE"
    )

    traversal_name: str = Field(max_length=255, nullable=False)

    # Relationships
    browser_config: "BrowserConfig" = Relationship()

    brain_states: List["BrainState"] = Relationship(cascade_delete=True)
    test_runs: List["TestRun"] = Relationship(cascade_delete=True)
    secret_values: List["SecretValue"] = Relationship(link_model=SecretValueTestTraversal)
