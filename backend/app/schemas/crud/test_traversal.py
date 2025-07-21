"""
TestTraversal CRUD Schemas

This module defines Pydantic models for TestTraversal entity CRUD operations.
Test traversals represent specific test execution paths with browser configurations.
"""

from datetime import datetime, timezone

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateTestTraversal(CreationModel):
    """
    Schema for creating a new test traversal.

    Test traversals represent specific test execution paths that combine
    a test case with a browser configuration. Each traversal belongs to
    a project and defines how a test should be executed.

    Attributes:
        id: Unique identifier generated using CUID
        project_id: Reference to the project this traversal belongs to
        test_case_id: Reference to the test case being executed
        browser_config_id: Reference to the browser configuration to use
        created_at: Timestamp when the traversal was created (UTC)
        traversal_name: Human-readable name for the test traversal
    """

    id: str = Field(default=CUID().generate())
    test_case_id: str
    browser_config_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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

    traversal_name: str

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
        project_id: Reference to the project this traversal belongs to
        test_case_id: Reference to the test case being executed
        browser_config_id: Reference to the browser configuration being used
        created_at: Timestamp when traversal was created
        traversal_name: Human-readable name for the test traversal
    """

    id: str
    test_case_id: str
    browser_config_id: str
    created_at: datetime
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


if __name__ == "__main__":
    # Demo: Generate and display sample test traversals
    rich_print(CreateTestTraversal.sample_factory_build())
    rich_print(UpdateTestTraversal.sample_factory_build())
    rich_print(ResponseTestTraversal.sample_factory_build())
