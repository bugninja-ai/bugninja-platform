"""
TestTraversal CRUD Schemas

This module defines Pydantic models for TestTraversal entity CRUD operations.
Test traversals represent specific test execution paths with browser configurations.
"""

from datetime import datetime, timezone
from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.communication.test_traversal import ExtendedResponseTestTraversal
from app.schemas.crud.base import CreationModel, PaginatedResponse, UpdateModel, faker


class CreateTestTraversal(CreationModel):
    """
    Schema for creating a new test traversal.

    Test traversals represent specific test execution paths that combine
    a test case with a browser configuration. Each traversal belongs to
    a project and defines how a test should be executed.

    Attributes:
        test_case_id: Reference to the test case being executed
        browser_config_id: Reference to the browser configuration to use
        traversal_name: Human-readable name for the test traversal
    """

    test_case_id: str
    browser_config_id: str
    traversal_name: str

    @classmethod
    def sample_factory_build(
        cls,
        test_case_id: str = CUID().generate(),
        browser_config_id: str = CUID().generate(),
    ) -> "CreateTestTraversal":
        """
        Generate a sample CreateTestTraversal instance for testing.

        Args:
            project_id: Project ID that the traversal belongs to
            test_case_id: Test case ID to execute
            browser_config_id: Browser configuration ID to use

        Returns:
            CreateTestTraversal: A sample test traversal with fake data
        """

        class CreateTestTraversalFactory(ModelFactory[CreateTestTraversal]):
            __model__ = CreateTestTraversal
            __faker__ = faker

            traversal_name = faker.catch_phrase()

        element = CreateTestTraversalFactory.build()
        element.test_case_id = test_case_id
        element.browser_config_id = browser_config_id

        return element


class UpdateTestTraversal(UpdateModel):
    """
    Schema for updating an existing test traversal.

    Allows updating the traversal name and automatically updates the timestamp.
    The relationships to project, test case, and browser config remain unchanged.

    Attributes:
        traversal_name: Updated name for the test traversal
    """

    traversal_name: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateTestTraversal":
        """
        Generate a sample UpdateTestTraversal instance for testing.

        Returns:
            UpdateTestTraversal: A sample update test traversal with fake data
        """

        class UpdateTestTraversalFactory(ModelFactory[UpdateTestTraversal]):
            __model__ = UpdateTestTraversal
            __faker__ = faker

            traversal_name = faker.catch_phrase()

        element = UpdateTestTraversalFactory.build()

        return element


class ResponseTestTraversal(BaseModel):
    """
    Schema for test traversal responses returned by the API.

    Contains all test traversal fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning test traversal data to clients.

    Attributes:
        id: Unique test traversal identifier
        test_case_id: Reference to the test case being executed
        browser_config_id: Reference to the browser configuration being used
        created_at: Timestamp when traversal was created
        updated_at: Timestamp when traversal was last updated
        traversal_name: Human-readable name for the test traversal
    """

    id: str
    test_case_id: str
    browser_config_id: str
    created_at: datetime
    updated_at: datetime
    traversal_name: str

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        test_case_id: str = CUID().generate(),
        browser_config_id: str = CUID().generate(),
    ) -> "ResponseTestTraversal":
        """
        Generate a sample ResponseTestTraversal instance for testing.

        Args:
            id: Test traversal ID to use in the sample
            project_id: Project ID that the traversal belongs to
            test_case_id: Test case ID being executed
            browser_config_id: Browser configuration ID being used

        Returns:
            ResponseTestTraversal: A sample response test traversal with fake data
        """

        class ResponseTestTraversalFactory(ModelFactory[ResponseTestTraversal]):
            __model__ = ResponseTestTraversal
            __faker__ = faker

            traversal_name = faker.catch_phrase()

        element = ResponseTestTraversalFactory.build()
        element.id = id
        element.test_case_id = test_case_id
        element.browser_config_id = browser_config_id

        return element


class PaginatedResponseTestTraversal(PaginatedResponse[ResponseTestTraversal]):
    """
    Paginated response schema for test traversals.

    This schema provides a standardized structure for paginated test traversal responses
    with metadata about the pagination state and the actual test traversal items.
    """

    @classmethod
    def sample_factory_build(
        cls,
        total_count: int = 25,
        page: int = 1,
        page_size: int = 10,
        test_case_id: Optional[str] = None,
    ) -> "PaginatedResponseTestTraversal":
        """
        Generate a sample PaginatedResponseTestTraversal instance for testing and documentation.

        Args:
            total_count: Total number of test traversals in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            test_case_id: Optional test case ID for filtering (default: None)

        Returns:
            PaginatedResponseTestTraversal: A sample paginated response with fake test traversal data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample test traversal items
        test_traversal_items = [
            ResponseTestTraversal.sample_factory_build(
                test_case_id=test_case_id or CUID().generate()
            )
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=test_traversal_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


class PaginatedResponseExtendedTestTraversal(PaginatedResponse[ExtendedResponseTestTraversal]):
    """
    Paginated response schema for extended test traversals.

    This schema provides a standardized structure for paginated extended test traversal responses
    with metadata about the pagination state and the actual extended test traversal items.
    """

    @classmethod
    def sample_factory_build(
        cls,
        total_count: int = 25,
        page: int = 1,
        page_size: int = 10,
        test_case_id: Optional[str] = None,
    ) -> "PaginatedResponseExtendedTestTraversal":
        """
        Generate a sample PaginatedResponseExtendedTestTraversal instance for testing and documentation.

        Args:
            total_count: Total number of test traversals in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            test_case_id: Optional test case ID for filtering (default: None)

        Returns:
            PaginatedResponseExtendedTestTraversal: A sample paginated response with fake extended test traversal data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample extended test traversal items
        extended_test_traversal_items = [
            ExtendedResponseTestTraversal.sample_factory_build(
                project_id=CUID().generate(),
                include_latest_run=True,
            )
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=extended_test_traversal_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


if __name__ == "__main__":
    # Demo: Generate and display sample test traversals
    rich_print(CreateTestTraversal.sample_factory_build())
    rich_print(UpdateTestTraversal.sample_factory_build())
    rich_print(ResponseTestTraversal.sample_factory_build())
