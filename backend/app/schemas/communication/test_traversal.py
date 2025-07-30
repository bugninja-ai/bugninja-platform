"""
Test Traversal Communication Schemas

This module defines Pydantic models for test traversal-related communication responses.
These schemas are used for API responses that include detailed test traversal information.
"""

from datetime import datetime
from typing import List, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.schemas.crud.base import faker
from app.schemas.crud.browser_config import ResponseBrowserConfig
from app.schemas.crud.test_run import RunState


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
    finished_at: Optional[datetime]

    @classmethod
    def sample_factory_build(cls, id: str = CUID().generate()) -> "LightResponseTestRun":
        """
        Generate a sample LightResponseTestRun instance for testing.

        Args:
            id: Test run ID to use in the sample

        Returns:
            LightResponseTestRun: A sample lightweight test run with fake data
        """

        class LightResponseTestRunFactory(ModelFactory[LightResponseTestRun]):
            __model__ = LightResponseTestRun
            __faker__ = faker

            state = faker.random_element([RunState.PENDING, RunState.FINISHED, RunState.FAILED])

        element = LightResponseTestRunFactory.build()
        element.id = id

        return element


class ExtendedResponseTestTraversal(BaseModel):
    """
    Extended test traversal response with comprehensive details.

    Contains full test traversal information including browser configuration
    and latest run details. Used for comprehensive test traversal data retrieval.

    Attributes:
        id: Unique test traversal identifier
        created_at: Timestamp when traversal was created
        traversal_name: Human-readable name for the test traversal
        browser_config: Full browser configuration details
        latest_run: Lightweight information about the most recent test run
    """

    id: str
    created_at: datetime
    traversal_name: str
    browser_config: ResponseBrowserConfig
    latest_run: Optional[LightResponseTestRun]

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        project_id: str = CUID().generate(),
        include_latest_run: bool = True,
    ) -> "ExtendedResponseTestTraversal":
        """
        Generate a sample ExtendedResponseTestTraversal instance for testing.

        Args:
            id: Test traversal ID to use in the sample
            project_id: Project ID to use for browser config
            include_latest_run: Whether to include a sample latest run

        Returns:
            ExtendedResponseTestTraversal: A sample extended test traversal response with fake data
        """

        class ExtendedResponseTestTraversalFactory(ModelFactory[ExtendedResponseTestTraversal]):
            __model__ = ExtendedResponseTestTraversal
            __faker__ = faker

            traversal_name = faker.catch_phrase()

        element = ExtendedResponseTestTraversalFactory.build()
        element.id = id

        # Generate browser config
        element.browser_config = ResponseBrowserConfig.sample_factory_build(project_id=project_id)

        # Generate optional latest run
        if include_latest_run:
            element.latest_run = LightResponseTestRun.sample_factory_build()
        else:
            element.latest_run = None

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample communication schemas
    rich_print("=== LightResponseTestRun Sample ===")
    rich_print(LightResponseTestRun.sample_factory_build())

    rich_print("\n=== ExtendedResponseTestTraversal Sample (with latest run) ===")
    rich_print(ExtendedResponseTestTraversal.sample_factory_build())

    rich_print("\n=== ExtendedResponseTestTraversal Sample (without latest run) ===")
    rich_print(ExtendedResponseTestTraversal.sample_factory_build(include_latest_run=False))
