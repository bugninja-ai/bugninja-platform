"""
Test Traversal Communication Schemas

This module defines Pydantic models for test traversal-related communication responses.
These schemas are used for API responses that include detailed test traversal information.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.crud.browser_config import ResponseBrowserConfig
from app.schemas.crud.secret_value import ResponseSecretValue
from app.schemas.crud.test_run import RunState


class LightResponseSecretValue(BaseModel):
    """
    Lightweight secret value response for test traversal communication.

    Contains essential secret value information without sensitive details,
    used when listing secrets within test traversal responses.

    Attributes:
        id: Unique secret value identifier
        secret_name: Human-readable name/identifier for the secret
    """

    id: str
    secret_name: str


class LightResponseTestRun(BaseModel):
    """
    Lightweight test run response for test traversal communication.

    Contains essential test run information without full execution details,
    used when listing test runs within test traversal responses.

    Attributes:
        id: Unique test run identifier
        state: Current state of the test run (STARTING, RUNNING, FINISHED)
        finished_at: Timestamp when the test run finished
    """

    id: str
    state: RunState
    finished_at: datetime


class ExtendedResponseTestTraversal(BaseModel):
    """
    Extended test traversal response with comprehensive details.

    Contains full test traversal information including browser configuration,
    latest run details, and associated secret values. Used for comprehensive
    test traversal data retrieval.

    Attributes:
        id: Unique test traversal identifier
        created_at: Timestamp when traversal was created
        traversal_name: Human-readable name for the test traversal
        browser_config: Full browser configuration details
        latest_run: Lightweight information about the most recent test run
        attached_secret_values: List of lightweight secret values associated with this traversal
    """

    id: str
    created_at: datetime
    traversal_name: str
    browser_config: ResponseBrowserConfig
    latest_run: Optional[LightResponseTestRun]
    attached_secret_values: List[LightResponseSecretValue]
