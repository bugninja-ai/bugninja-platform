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
from app.schemas.crud.base import CreationModel, UpdateModel, faker


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


if __name__ == "__main__":
    # Demo: Generate and display sample test cases
    rich_print(CreateTestCase.sample_factory_build())
    rich_print(UpdateTestCase.sample_factory_build())
    rich_print(ResponseTestCase.sample_factory_build())
