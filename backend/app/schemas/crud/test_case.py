"""
TestCase CRUD Schemas

This module defines Pydantic models for TestCase entity CRUD operations.
Test cases represent specific testing scenarios that can be associated with documents
and projects, containing test configuration and validation rules.
"""

from datetime import datetime, timezone
from typing import List, Optional

from cuid2 import Cuid as CUID
from faker import Faker
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, ConfigDict, Field
from rich import print as rich_print

from app.db.test_case import TestCasePriority
from app.schemas.communication.test_case import ExtendedResponseTestcase
from app.schemas.crud.base import CreationModel, PaginatedResponse, UpdateModel, faker
from app.schemas.crud.browser_config import CreateBrowserConfig, ResponseBrowserConfig
from app.schemas.crud.secret_value import CreateSecretValue, ResponseSecretValue
from app.schemas.crud.test_traversal import ResponseTestTraversal


class CreateTestCase(CreationModel):
    """
    Schema for creating a new test case.

    Test cases define specific testing scenarios with configuration details
    including test goals, rules, and domain restrictions. Each test case
    belongs to a project and is associated with a document.

    Attributes:
        project_id: Required reference to the project this test case belongs to
        document_id: Optional reference to the document this test case is based on
        test_name: Human-readable name for the test case
        test_description: Detailed description of what the test case does
        test_goal: Specific objective or goal of this test case
        extra_rules: Additional rules or constraints for the test
        url_route: The URL route/path that this test case targets
        allowed_domains: List of domains that are allowed for this test case
        priority: Priority level of the test case (low, medium, high, critical)
        category: Optional category for organizing test cases
    """

    project_id: str
    document_id: Optional[str]
    test_name: str
    test_description: str
    test_goal: str
    extra_rules: str
    url_route: str
    allowed_domains: List[str]
    priority: TestCasePriority
    category: Optional[str] = None

    # New browser configs to create
    new_browser_configs: Optional[List[CreateBrowserConfig]] = None

    # Existing browser config IDs to associate
    existing_browser_config_ids: Optional[List[str]] = None

    # New secret values to create
    new_secret_values: Optional[List[CreateSecretValue]] = None

    # Existing secret value IDs to associate
    existing_secret_value_ids: Optional[List[str]] = None

    @classmethod
    def sample_factory_build(
        cls, project_id: str = CUID().generate(), document_id: Optional[str] = None
    ) -> "CreateTestCase":
        """
        Generate a sample CreateTestCase instance for testing.

        Args:
            project_id: Project ID that the test case belongs to
            document_id: Document ID that the test case is based on

        Returns:
            CreateTestCase: A sample test case with fake data
        """

        class CreateTestCaseFactory(ModelFactory[CreateTestCase]):
            __model__ = CreateTestCase
            __faker__ = faker

            test_name = faker.user_name()
            test_description = faker.paragraph()
            test_goal = faker.paragraph()
            extra_rules = faker.sentence()
            url_route = faker.url()
            allowed_domains = [faker.url() for _ in range(3)]
            priority = faker.random_element(
                [
                    TestCasePriority.LOW,
                    TestCasePriority.MEDIUM,
                    TestCasePriority.HIGH,
                    TestCasePriority.CRITICAL,
                ]
            )
            category = faker.random_element(
                ["login", "payment", "search", "navigation", "profile", "settings", "general"]
            )

        element = CreateTestCaseFactory.build()

        element.project_id = project_id
        element.document_id = document_id

        return element


class UpdateTestCase(UpdateModel):
    """
    Schema for updating an existing test case.

    Allows updating all test case fields except ID and relationships.
    Automatically updates the timestamp when modified.

    Attributes:
        test_name: Updated name for the test case
        test_description: Updated description of the test case
        test_goal: Updated goal/objective of the test case
        extra_rules: Updated additional rules or constraints
        url_route: Updated URL route/path target
        allowed_domains: Updated list of allowed domains
        priority: Updated priority level of the test case
        category: Updated category for organizing test cases
    """

    test_name: Optional[str] = None
    test_description: Optional[str] = None
    test_goal: Optional[str] = None
    extra_rules: Optional[str] = None
    url_route: Optional[str] = None
    allowed_domains: Optional[List[str]] = None
    priority: Optional[TestCasePriority] = None
    category: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateTestCase":
        """
        Generate a sample UpdateTestCase instance for testing.

        Returns:
            UpdateTestCase: A sample update test case with fake data
        """

        class UpdateTestCaseFactory(ModelFactory[UpdateTestCase]):
            __model__ = UpdateTestCase
            __faker__ = faker

            test_name = faker.user_name()
            test_description = faker.paragraph()
            test_goal = faker.paragraph()
            extra_rules = faker.sentence()
            url_route = faker.url()
            allowed_domains = [faker.url() for _ in range(3)]
            priority = faker.random_element(
                [
                    TestCasePriority.LOW,
                    TestCasePriority.MEDIUM,
                    TestCasePriority.HIGH,
                    TestCasePriority.CRITICAL,
                ]
            )
            category = faker.random_element(
                ["login", "payment", "search", "navigation", "profile", "settings", "general"]
            )

        element = UpdateTestCaseFactory.build()

        return element


class ResponseTestCase(BaseModel):
    """
    Schema for test case responses returned by the API.

    Contains all test case fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning test case data to clients.

    Attributes:
        id: Unique test case identifier
        project_id: Reference to the project this test case belongs to
        document_id: Reference to the document this test case is based on
        created_at: Timestamp when test case was created
        updated_at: Timestamp when test case was last updated
        test_name: Human-readable name for the test case
        test_description: Detailed description of the test case
        test_goal: Specific objective of the test case
        extra_rules: Additional rules or constraints
        url_route: URL route/path target
        allowed_domains: List of allowed domains for this test case
        priority: Priority level of the test case
        category: Category for organizing test cases
    """

    id: str
    project_id: str
    document_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    test_name: str
    test_description: str
    test_goal: str
    extra_rules: str
    url_route: str
    allowed_domains: List[str]
    priority: TestCasePriority
    category: Optional[str]

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        project_id: str = CUID().generate(),
        document_id: str = CUID().generate(),
    ) -> "ResponseTestCase":
        """
        Generate a sample ResponseTestCase instance for testing.

        Args:
            id: Test case ID to use in the sample
            project_id: Project ID that the test case belongs to
            document_id: Document ID that the test case is based on

        Returns:
            ResponseTestCase: A sample response test case with fake data
        """

        class ResponseTestCaseFactory(ModelFactory[ResponseTestCase]):
            __model__ = ResponseTestCase
            __faker__ = faker

            test_name = faker.user_name()
            test_description = faker.paragraph()
            test_goal = faker.paragraph()
            extra_rules = faker.sentence()
            url_route = faker.url()
            allowed_domains = [faker.url() for _ in range(3)]
            priority = faker.random_element(
                [
                    TestCasePriority.LOW,
                    TestCasePriority.MEDIUM,
                    TestCasePriority.HIGH,
                    TestCasePriority.CRITICAL,
                ]
            )
            category = faker.random_element(
                ["login", "payment", "search", "navigation", "profile", "settings", "general"]
            )

        element = ResponseTestCaseFactory.build()
        element.id = id
        element.project_id = project_id
        element.document_id = document_id

        return element


class PaginatedResponseTestCase(PaginatedResponse[ResponseTestCase]):
    """
    Paginated response schema for test cases.

    This schema provides a standardized structure for paginated test case responses
    with metadata about the pagination state and the actual test case items.
    """

    @classmethod
    def sample_factory_build(
        cls,
        total_count: int = 25,
        page: int = 1,
        page_size: int = 10,
        project_id: Optional[str] = None,
    ) -> "PaginatedResponseTestCase":
        """
        Generate a sample PaginatedResponseTestCase instance for testing and documentation.

        Args:
            total_count: Total number of test cases in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            project_id: Optional project ID for filtering (default: None)

        Returns:
            PaginatedResponseTestCase: A sample paginated response with fake test case data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample test case items
        test_case_items = [
            ResponseTestCase.sample_factory_build(project_id=project_id or CUID().generate())
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=test_case_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


class PaginatedResponseExtendedTestCase(PaginatedResponse[ExtendedResponseTestcase]):
    """
    Paginated response schema for extended test cases.

    This schema provides a standardized structure for paginated extended test case responses
    with metadata about the pagination state and the actual extended test case items.
    """

    @classmethod
    def sample_factory_build(
        cls,
        total_count: int = 25,
        page: int = 1,
        page_size: int = 10,
        project_id: Optional[str] = None,
    ) -> "PaginatedResponseExtendedTestCase":
        """
        Generate a sample PaginatedResponseExtendedTestCase instance for testing and documentation.

        Args:
            total_count: Total number of test cases in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            project_id: Optional project ID for filtering (default: None)

        Returns:
            PaginatedResponseExtendedTestCase: A sample paginated response with fake extended test case data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample extended test case items
        extended_test_case_items = [
            ExtendedResponseTestcase.sample_factory_build(
                project_id=project_id or CUID().generate(),
                include_document=True,
                include_browser_configs=True,
            )
            for _ in range(items_in_page)
        ]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=extended_test_case_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


class CreateTestCaseResponse(BaseModel):
    """
    Response schema for enhanced test case creation.

    Contains all created and associated entities when creating a test case
    with browser configs, secret values, and test traversals.

    Attributes:
        test_case: The created test case
        created_browser_configs: List of newly created browser configurations
        associated_browser_configs: List of existing browser configurations that were associated
        created_secret_values: List of newly created secret values
        associated_secret_values: List of existing secret values that were associated
        created_test_traversals: List of created test traversals (one per browser config)
    """

    test_case: ResponseTestCase
    created_browser_configs: List[ResponseBrowserConfig]
    associated_browser_configs: List[ResponseBrowserConfig]
    created_secret_values: List[ResponseSecretValue]
    associated_secret_values: List[ResponseSecretValue]
    created_test_traversals: List[ResponseTestTraversal]

    @classmethod
    def sample_factory_build(
        cls,
        test_case_id: str = CUID().generate(),
        project_id: str = CUID().generate(),
    ) -> "CreateTestCaseResponse":
        """
        Generate a sample CreateTestCaseResponse instance for testing and documentation.

        Args:
            test_case_id: Test case ID to use in the sample
            project_id: Project ID to use in the sample

        Returns:
            CreateTestCaseResponse: A sample response with fake data
        """
        return cls(
            test_case=ResponseTestCase.sample_factory_build(id=test_case_id, project_id=project_id),
            created_browser_configs=[
                ResponseBrowserConfig.sample_factory_build(project_id=project_id) for _ in range(2)
            ],
            associated_browser_configs=[
                ResponseBrowserConfig.sample_factory_build(project_id=project_id) for _ in range(1)
            ],
            created_secret_values=[
                ResponseSecretValue.sample_factory_build(project_id=project_id) for _ in range(2)
            ],
            associated_secret_values=[
                ResponseSecretValue.sample_factory_build(project_id=project_id) for _ in range(1)
            ],
            created_test_traversals=[
                ResponseTestTraversal.sample_factory_build(
                    test_case_id=test_case_id,
                    browser_config_id=CUID().generate(),
                )
                for _ in range(3)
            ],
        )


if __name__ == "__main__":
    # Demo: Generate and display sample test cases
    rich_print(CreateTestCase.sample_factory_build())
    rich_print(UpdateTestCase.sample_factory_build())
    rich_print(ResponseTestCase.sample_factory_build())
    rich_print(CreateTestCaseResponse.sample_factory_build())
