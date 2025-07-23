"""
Test Run Communication Schemas

This module defines Pydantic models for test run-related communication responses.
These schemas are used for API responses that include detailed test run information.
"""

from datetime import datetime
from typing import List, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.db.test_run import RunOrigin, RunState, RunType
from app.schemas.crud.base import faker
from app.schemas.crud.browser_config import ResponseBrowserConfig
from app.schemas.crud.history_element import ResponseHistoryElement


class ExtendedResponseTestRun(BaseModel):
    """
    Extended test run response with comprehensive details.

    Contains full test run information including browser configuration,
    execution history, and detailed tracking information. Used for comprehensive
    test run data retrieval.

    Attributes:
        id: Unique test run identifier
        test_traversal_id: Reference to the test traversal being executed
        browser_config: Full browser configuration details
        run_type: Type of test run (AGENTIC, REPLAY, REPLAY_WITH_HEALING)
        origin: Origin of the test run (USER or CICD)
        repair_was_needed: Whether repair/healing was needed during execution
        started_at: Timestamp when the test run started
        finished_at: Timestamp when the test run finished
        current_state: Current state of the test run
        history: List of history elements tracking the execution
        run_gif: URL or path to the animated GIF of the test run
    """

    id: str
    test_traversal_id: str
    browser_config: ResponseBrowserConfig
    run_type: RunType
    origin: RunOrigin
    repair_was_needed: bool
    started_at: datetime
    finished_at: Optional[datetime]
    current_state: RunState
    history: List[ResponseHistoryElement]
    run_gif: str

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        test_traversal_id: str = CUID().generate(),
        project_id: str = CUID().generate(),
        include_history: bool = True,
        history_count: int = 4,
    ) -> "ExtendedResponseTestRun":
        """
        Generate a sample ExtendedResponseTestRun instance for testing.

        Args:
            id: Test run ID to use in the sample
            test_traversal_id: Test traversal ID being executed
            project_id: Project ID to use for browser config
            include_history: Whether to include sample history elements
            history_count: Number of history elements to generate

        Returns:
            ExtendedResponseTestRun: A sample extended test run response with fake data
        """

        class ExtendedResponseTestRunFactory(ModelFactory[ExtendedResponseTestRun]):
            __model__ = ExtendedResponseTestRun
            __faker__ = faker

            run_type = faker.random_element(
                [RunType.AGENTIC, RunType.REPLAY, RunType.REPLAY_WITH_HEALING]
            )
            origin = faker.random_element([RunOrigin.USER, RunOrigin.CICD])
            repair_was_needed = faker.boolean()
            started_at = faker.date_time()
            finished_at = faker.date_time()
            current_state = faker.random_element(
                [RunState.STARTING, RunState.RUNNING, RunState.FINISHED]
            )
            run_gif = faker.image_url()

        element = ExtendedResponseTestRunFactory.build()
        element.id = id
        element.test_traversal_id = test_traversal_id

        # Generate browser config
        element.browser_config = ResponseBrowserConfig.sample_factory_build(project_id=project_id)

        # Generate history elements
        if include_history:
            element.history = [
                ResponseHistoryElement.sample_factory_build(test_run_id=id)
                for _ in range(history_count)
            ]
        else:
            element.history = []

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample communication schemas
    rich_print("=== ExtendedResponseTestRun Sample (with history) ===")
    rich_print(ExtendedResponseTestRun.sample_factory_build())

    rich_print("\n=== ExtendedResponseTestRun Sample (without history) ===")
    rich_print(ExtendedResponseTestRun.sample_factory_build(include_history=False))
