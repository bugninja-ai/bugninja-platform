"""
TestRun CRUD Schemas

This module defines Pydantic models for TestRun entity CRUD operations.
Test runs represent actual executions of test traversals with detailed tracking.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.db.test_run import RunOrigin, RunState, RunType
from app.schemas.crud.base import CreationModel, UpdateModel, faker
from app.schemas.crud.history_element import ResponseHistoryElement


class CreateTestRun(CreationModel):
    """
    Schema for creating a new test run.

    Test runs represent actual executions of test traversals with detailed tracking
    of the execution process, timing, and outcomes. Each test run can have different
    types and origins, and tracks the complete execution history.

    Attributes:
        test_traversal_id: Reference to the test traversal being executed
        browser_config_id: Reference to the browser configuration being used
        run_type: Type of test run (AGENTIC, REPLAY, REPLAY_WITH_HEALING)
        origin: Origin of the test run (USER or CICD)
        repair_was_needed: Whether repair/healing was needed during execution
        current_state: Current state of the test run
        run_gif: URL or path to the animated GIF of the test run
    """

    test_traversal_id: str
    browser_config_id: str
    run_type: RunType
    origin: RunOrigin
    repair_was_needed: bool
    current_state: RunState
    run_gif: str

    @classmethod
    def sample_factory_build(
        cls,
        test_traversal_id: str = CUID().generate(),
        browser_config_id: str = CUID().generate(),
    ) -> "CreateTestRun":
        """
        Generate a sample CreateTestRun instance for testing.

        Args:
            test_traversal_id: Test traversal ID being executed
            browser_config_id: Browser configuration ID being used

        Returns:
            CreateTestRun: A sample test run with fake data
        """

        class CreateTestRunFactory(ModelFactory[CreateTestRun]):
            __model__ = CreateTestRun
            __faker__ = faker

            run_type = faker.random_element(
                [RunType.AGENTIC, RunType.REPLAY, RunType.REPLAY_WITH_HEALING]
            )
            origin = faker.random_element([RunOrigin.USER, RunOrigin.CICD])
            repair_was_needed = faker.boolean()
            current_state = faker.random_element(
                [RunState.STARTING, RunState.RUNNING, RunState.FINISHED]
            )
            history = [
                {"action": "click", "element": "button", "timestamp": faker.date_time().isoformat()}
                for _ in range(3)
            ]
            run_gif = faker.image_url()

        element = CreateTestRunFactory.build()
        element.test_traversal_id = test_traversal_id
        element.browser_config_id = browser_config_id

        return element


class UpdateTestRun(UpdateModel):
    """
    Schema for updating an existing test run.

    Allows updating test run state, timing, and execution details.
    The relationships to test traversal and browser config remain unchanged.

    Attributes:
        cost_id: Updated reference to the cost record
        repair_was_needed: Updated repair status
        finished_at: Updated timestamp when the test run finished
        current_state: Updated current state of the test run
        history: Updated list of history elements
        run_gif: Updated URL or path to the animated GIF
    """

    repair_was_needed: Optional[bool] = None
    finished_at: Optional[datetime] = None
    current_state: Optional[RunState] = None
    run_gif: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateTestRun":
        """
        Generate a sample UpdateTestRun instance for testing.

        Returns:
            UpdateTestRun: A sample update test run with fake data
        """

        class UpdateTestRunFactory(ModelFactory[UpdateTestRun]):
            __model__ = UpdateTestRun
            __faker__ = faker

            repair_was_needed = faker.boolean()
            finished_at = faker.date_time()
            current_state = faker.random_element(
                [RunState.STARTING, RunState.RUNNING, RunState.FINISHED]
            )
            history = [
                {"action": "type", "element": "input", "timestamp": faker.date_time().isoformat()}
                for _ in range(5)
            ]
            run_gif = faker.image_url()

        element = UpdateTestRunFactory.build()

        return element


class ResponseTestRun(BaseModel):
    """
    Schema for test run responses returned by the API.

    Contains all test run fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning test run data to clients.

    Attributes:
        id: Unique test run identifier
        test_traversal_id: Reference to the test traversal being executed
        browser_config_id: Reference to the browser configuration being used
        cost_id: Optional reference to the cost record for this run
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
    browser_config_id: str
    run_type: RunType
    origin: RunOrigin
    repair_was_needed: bool
    started_at: datetime
    finished_at: datetime
    current_state: RunState
    history: List[ResponseHistoryElement]
    run_gif: str

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        test_traversal_id: str = CUID().generate(),
        browser_config_id: str = CUID().generate(),
    ) -> "ResponseTestRun":
        """
        Generate a sample ResponseTestRun instance for testing.

        Args:
            id: Test run ID to use in the sample
            test_traversal_id: Test traversal ID being executed
            browser_config_id: Browser configuration ID being used

        Returns:
            ResponseTestRun: A sample response test run with fake data
        """

        class ResponseTestRunFactory(ModelFactory[ResponseTestRun]):
            __model__ = ResponseTestRun
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
            history = [
                {"action": "scroll", "element": "page", "timestamp": faker.date_time().isoformat()}
                for _ in range(4)
            ]
            run_gif = faker.image_url()

        element = ResponseTestRunFactory.build()
        element.id = id
        element.test_traversal_id = test_traversal_id
        element.browser_config_id = browser_config_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample test runs
    rich_print(CreateTestRun.sample_factory_build())
    rich_print(UpdateTestRun.sample_factory_build())
    rich_print(ResponseTestRun.sample_factory_build())
