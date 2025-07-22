"""
Cost CRUD Schemas

This module defines Pydantic models for Cost entity CRUD operations.
Cost entities track AI model usage costs and token consumption for test runs.
"""

from datetime import datetime
from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateCost(CreationModel):
    """
    Schema for creating a new cost record.

    Cost records track AI model usage costs and token consumption for test runs.
    Each cost record is associated with a specific test run and project,
    tracking the financial impact of AI-powered testing.

    Attributes:
        test_run_id: Reference to the test run this cost belongs to
        project_id: Reference to the project this cost belongs to
        model_type: Type of AI model used (e.g., "gpt-4", "claude-3")
        cost_per_token: Cost per token in dollars
        input_token_num: Number of input tokens consumed
        completion_token_num: Number of completion tokens generated
        cost_in_dollars: Total cost in dollars for this usage
    """

    test_run_id: str
    project_id: str
    model_type: str
    cost_per_token: float
    input_token_num: int
    completion_token_num: int
    cost_in_dollars: float

    @classmethod
    def sample_factory_build(
        cls, test_run_id: str = CUID().generate(), project_id: str = CUID().generate()
    ) -> "CreateCost":
        """
        Generate a sample CreateCost instance for testing.

        Args:
            test_run_id: Test run ID that the cost belongs to
            project_id: Project ID that the cost belongs to

        Returns:
            CreateCost: A sample cost record with fake data
        """

        class CreateCostFactory(ModelFactory[CreateCost]):
            __model__ = CreateCost
            __faker__ = faker

            model_type = faker.random_element(["gpt-4", "claude-3", "gpt-3.5-turbo"])
            cost_per_token = faker.pyfloat(min_value=0.0001, max_value=0.01, right_digits=6)
            input_token_num = faker.random_int(min=100, max=10000)
            completion_token_num = faker.random_int(min=50, max=5000)
            cost_in_dollars = faker.pyfloat(min_value=0.01, max_value=10.0, right_digits=4)

        element = CreateCostFactory.build()
        element.test_run_id = test_run_id
        element.project_id = project_id

        return element


class UpdateCost(UpdateModel):
    """
    Schema for updating an existing cost record.

    Allows updating cost-related fields and automatically updates the timestamp.
    The relationships to test run and project remain unchanged.

    Attributes:
        model_type: Updated type of AI model used
        cost_per_token: Updated cost per token in dollars
        input_token_num: Updated number of input tokens consumed
        completion_token_num: Updated number of completion tokens generated
        cost_in_dollars: Updated total cost in dollars
    """

    model_type: Optional[str] = None
    cost_per_token: Optional[float] = None
    input_token_num: Optional[int] = None
    completion_token_num: Optional[int] = None
    cost_in_dollars: Optional[float] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateCost":
        """
        Generate a sample UpdateCost instance for testing.

        Returns:
            UpdateCost: A sample update cost record with fake data
        """

        class UpdateCostFactory(ModelFactory[UpdateCost]):
            __model__ = UpdateCost
            __faker__ = faker

            model_type = faker.random_element(["gpt-4", "claude-3", "gpt-3.5-turbo"])
            cost_per_token = faker.pyfloat(min_value=0.0001, max_value=0.01, right_digits=6)
            input_token_num = faker.random_int(min=100, max=10000)
            completion_token_num = faker.random_int(min=50, max=5000)
            cost_in_dollars = faker.pyfloat(min_value=0.01, max_value=10.0, right_digits=4)

        element = UpdateCostFactory.build()

        return element


class ResponseCost(BaseModel):
    """
    Schema for cost responses returned by the API.

    Contains all cost fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning cost data to clients.

    Attributes:
        id: Unique cost record identifier
        test_run_id: Reference to the test run this cost belongs to
        project_id: Reference to the project this cost belongs to
        created_at: Timestamp when cost record was created
        model_type: Type of AI model used
        cost_per_token: Cost per token in dollars
        input_token_num: Number of input tokens consumed
        completion_token_num: Number of completion tokens generated
        cost_in_dollars: Total cost in dollars for this usage
    """

    id: str
    test_run_id: str
    project_id: str
    created_at: datetime
    model_type: str
    cost_per_token: float
    input_token_num: int
    completion_token_num: int
    cost_in_dollars: float

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        test_run_id: str = CUID().generate(),
        project_id: str = CUID().generate(),
    ) -> "ResponseCost":
        """
        Generate a sample ResponseCost instance for testing.

        Args:
            id: Cost record ID to use in the sample
            test_run_id: Test run ID that the cost belongs to
            project_id: Project ID that the cost belongs to

        Returns:
            ResponseCost: A sample response cost record with fake data
        """

        class ResponseCostFactory(ModelFactory[ResponseCost]):
            __model__ = ResponseCost
            __faker__ = faker

            model_type = faker.random_element(["gpt-4", "claude-3", "gpt-3.5-turbo"])
            cost_per_token = faker.pyfloat(min_value=0.0001, max_value=0.01, right_digits=6)
            input_token_num = faker.random_int(min=100, max=10000)
            completion_token_num = faker.random_int(min=50, max=5000)
            cost_in_dollars = faker.pyfloat(min_value=0.01, max_value=10.0, right_digits=4)

        element = ResponseCostFactory.build()
        element.id = id
        element.test_run_id = test_run_id
        element.project_id = project_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample cost records
    rich_print(CreateCost.sample_factory_build())
    rich_print(UpdateCost.sample_factory_build())
    rich_print(ResponseCost.sample_factory_build())
