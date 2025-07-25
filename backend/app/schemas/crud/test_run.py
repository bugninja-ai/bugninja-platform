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
from app.schemas.communication.test_run import ExtendedResponseTestRun
from app.schemas.crud.base import CreationModel, PaginatedResponse, UpdateModel, faker
from app.schemas.crud.browser_config import ResponseBrowserConfig
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
    browser_config_id: Optional[str]
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
            history = [ResponseHistoryElement.sample_factory_build() for _ in range(4)]
            run_gif = faker.image_url()

        element = ResponseTestRunFactory.build()
        element.id = id
        element.test_traversal_id = test_traversal_id
        element.browser_config_id = browser_config_id

        return element


class PaginatedResponseTestRun(PaginatedResponse[ResponseTestRun]):
    """
    Paginated response schema for test runs.

    This schema provides a standardized structure for paginated test run responses
    with metadata about the pagination state and the actual test run items.
    """

    @classmethod
    def sample_factory_build(
        cls,
        total_count: int = 25,
        page: int = 1,
        page_size: int = 10,
        test_traversal_id: Optional[str] = None,
    ) -> "PaginatedResponseTestRun":
        """
        Generate a sample PaginatedResponseTestRun instance for testing and documentation.

        Args:
            total_count: Total number of test runs in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            test_traversal_id: Optional test traversal ID for filtering (default: None)

        Returns:
            PaginatedResponseTestRun: A sample paginated response with fake test run data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample test run items
        test_run_items = [
            ResponseTestRun.sample_factory_build(
                test_traversal_id=test_traversal_id or CUID().generate()
            )
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=test_run_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


class PaginatedResponseExtendedTestRun(PaginatedResponse[ExtendedResponseTestRun]):
    """
    Paginated response schema for extended test runs.

    This schema provides a standardized structure for paginated extended test run responses
    with metadata about the pagination state and the actual extended test run items.
    """

    @classmethod
    def sample_factory_build(
        cls,
        total_count: int = 25,
        page: int = 1,
        page_size: int = 10,
        test_traversal_id: Optional[str] = None,
    ) -> "PaginatedResponseExtendedTestRun":
        """
        Generate a sample PaginatedResponseExtendedTestRun instance for testing and documentation.

        Args:
            total_count: Total number of test runs in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            test_traversal_id: Optional test traversal ID for filtering (default: None)

        Returns:
            PaginatedResponseExtendedTestRun: A sample paginated response with fake extended test run data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample extended test run items
        extended_test_run_items = [
            ExtendedResponseTestRun.sample_factory_build(
                test_traversal_id=test_traversal_id or CUID().generate(),
                include_history=True,
                history_count=3,
            )
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=extended_test_run_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


class PaginatedResponseTestRunsByTestCase(PaginatedResponse[ExtendedResponseTestRun]):
    """
    Paginated response schema for test runs by test case.

    This schema provides a standardized structure for paginated test run responses
    filtered by test case, with metadata about the pagination state, test case information,
    and the actual extended test run items.
    """

    test_case_id: str
    test_case_name: str

    @classmethod
    def sample_factory_build(
        cls,
        test_case_id: str = CUID().generate(),
        test_case_name: str = "Sample Test Case",
        total_count: int = 15,
        page: int = 1,
        page_size: int = 10,
    ) -> "PaginatedResponseTestRunsByTestCase":
        """
        Generate a sample PaginatedResponseTestRunsByTestCase instance for testing and documentation.

        Args:
            test_case_id: Test case ID for the response (default: generated CUID)
            test_case_name: Test case name for the response (default: "Sample Test Case")
            total_count: Total number of test runs for the test case (default: 15)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)

        Returns:
            PaginatedResponseTestRunsByTestCase: A sample paginated response with fake test run data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample extended test run items
        extended_test_run_items = [
            ExtendedResponseTestRun.sample_factory_build(
                test_traversal_id=CUID().generate(),
                project_id=CUID().generate(),
            )
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=extended_test_run_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            test_case_id=test_case_id,
            test_case_name=test_case_name,
        )


if __name__ == "__main__":
    # Demo: Generate and display sample test runs
    rich_print(CreateTestRun.sample_factory_build())
    rich_print(UpdateTestRun.sample_factory_build())
    rich_print(ResponseTestRun.sample_factory_build())
