"""
BrainState CRUD Schemas

This module defines Pydantic models for BrainState entity CRUD operations.
Brain states represent the AI agent's cognitive state during test execution.
"""

from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateBrainState(CreationModel):
    """
    Schema for creating a new brain state.

    Brain states represent the AI agent's cognitive state during test execution.
    Each brain state contains the agent's current understanding, memory,
    and next goals for the test run.

    Attributes:
        test_traversal_id: Reference to the test run this brain state belongs to
        idx_in_run: Index position within the run sequence
        valid: Whether this brain state is valid and usable
        evaluation_previous_goal: Evaluation of the previous goal's success
        memory: Current memory/context of the AI agent
        next_goal: The next goal or objective for the agent
    """

    test_traversal_id: str
    idx_in_run: int
    valid: bool
    evaluation_previous_goal: str
    memory: str
    next_goal: str

    @classmethod
    def sample_factory_build(
        cls, test_traversal_id: str = CUID().generate(), brain_state_idx: int = 0
    ) -> "CreateBrainState":
        """
        Generate a sample CreateBrainState instance for testing.

        Args:
            test_traversal_id: Test run ID that the brain state belongs to

        Returns:
            CreateBrainState: A sample brain state with fake data
        """

        class CreateBrainStateFactory(ModelFactory[CreateBrainState]):
            __model__ = CreateBrainState
            __faker__ = faker

            idx_in_run = faker.random_int(min=0, max=100)
            valid = faker.boolean()
            evaluation_previous_goal = faker.sentence()
            memory = faker.paragraph()
            next_goal = faker.sentence()

        element = CreateBrainStateFactory.build()
        element.test_traversal_id = test_traversal_id
        element.idx_in_run = brain_state_idx

        return element


class UpdateBrainState(UpdateModel):
    """
    Schema for updating an existing brain state.

    Allows updating all brain state fields except ID and test run relationship.

    Attributes:
        idx_in_run: Updated index position within the run sequence
        valid: Updated validity status
        evaluation_previous_goal: Updated evaluation of the previous goal
        memory: Updated memory/context of the AI agent
        next_goal: Updated next goal or objective for the agent
    """

    idx_in_run: Optional[int] = None
    valid: Optional[bool] = None
    evaluation_previous_goal: Optional[str] = None
    memory: Optional[str] = None
    next_goal: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateBrainState":
        """
        Generate a sample UpdateBrainState instance for testing.

        Returns:
            UpdateBrainState: A sample update brain state with fake data
        """

        class UpdateBrainStateFactory(ModelFactory[UpdateBrainState]):
            __model__ = UpdateBrainState
            __faker__ = faker

            idx_in_run = faker.random_int(min=0, max=100)
            valid = faker.boolean()
            evaluation_previous_goal = faker.sentence()
            memory = faker.paragraph()
            next_goal = faker.sentence()

        element = UpdateBrainStateFactory.build()

        return element


class ResponseBrainState(BaseModel):
    """
    Schema for brain state responses returned by the API.

    Contains all brain state fields including read-only fields like ID.
    Used for GET operations and when returning brain state data to clients.

    Attributes:
        id: Unique brain state identifier
        test_traversal_id: Reference to the test run this brain state belongs to
        idx_in_run: Index position within the run sequence
        valid: Whether this brain state is valid and usable
        evaluation_previous_goal: Evaluation of the previous goal's success
        memory: Current memory/context of the AI agent
        next_goal: The next goal or objective for the agent
    """

    id: str
    test_traversal_id: str
    idx_in_run: int
    valid: bool
    evaluation_previous_goal: str
    memory: str
    next_goal: str

    @classmethod
    def sample_factory_build(
        cls, id: str = CUID().generate(), test_traversal_id: str = CUID().generate()
    ) -> "ResponseBrainState":
        """
        Generate a sample ResponseBrainState instance for testing.

        Args:
            id: Brain state ID to use in the sample
            test_traversal_id: Test run ID that the brain state belongs to

        Returns:
            ResponseBrainState: A sample response brain state with fake data
        """

        class ResponseBrainStateFactory(ModelFactory[ResponseBrainState]):
            __model__ = ResponseBrainState
            __faker__ = faker

            idx_in_run = faker.random_int(min=0, max=100)
            valid = faker.boolean()
            evaluation_previous_goal = faker.sentence()
            memory = faker.paragraph()
            next_goal = faker.sentence()

        element = ResponseBrainStateFactory.build()
        element.id = id
        element.test_traversal_id = test_traversal_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample brain states
    rich_print(CreateBrainState.sample_factory_build())
    rich_print(UpdateBrainState.sample_factory_build())
    rich_print(ResponseBrainState.sample_factory_build())
