"""
Action CRUD Schemas

This module defines Pydantic models for Action entity CRUD operations.
Actions represent specific UI interactions performed by the AI agent during test execution.
"""

from typing import Any, Dict, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker
from app.schemas.crud.utils import generate_action_data, generate_dom_element_data


class CreateAction(CreationModel):
    """
    Schema for creating a new action.

    Actions represent specific UI interactions performed by the AI agent during test execution.
    Each action is associated with a brain state and contains details about the interaction
    including the action type and DOM element data.

    Attributes:
        brain_state_id: Reference to the brain state this action belongs to
        idx_in_brain_state: Index position within the brain state's action sequence
        action: Dictionary containing action details (type, parameters, etc.)
        dom_element_data: Dictionary containing DOM element information
        valid: Whether this action is valid and executable
    """

    brain_state_id: str
    idx_in_brain_state: int
    action: Dict[str, Any]
    dom_element_data: Dict[str, Any]
    valid: bool

    @classmethod
    def sample_factory_build(
        cls, brain_state_id: str = CUID().generate(), idx_in_brain_state: int = 0
    ) -> "CreateAction":
        """
        Generate a sample CreateAction instance for testing.

        Args:
            brain_state_id: Brain state ID that the action belongs to

        Returns:
            CreateAction: A sample action with fake data
        """

        class CreateActionFactory(ModelFactory[CreateAction]):
            __model__ = CreateAction
            __faker__ = faker

            idx_in_brain_state = faker.random_int(min=0, max=50)
            action = generate_action_data(faker)
            dom_element_data = generate_dom_element_data(faker, "input")
            valid = faker.boolean()

        element = CreateActionFactory.build()
        element.brain_state_id = brain_state_id
        element.idx_in_brain_state = idx_in_brain_state

        return element


class UpdateAction(UpdateModel):
    """
    Schema for updating an existing action.

    Allows updating all action fields except ID and brain state relationship.

    Attributes:
        idx_in_brain_state: Updated index position within the brain state's action sequence
        action: Updated action details dictionary
        dom_element_data: Updated DOM element information dictionary
        valid: Updated validity status
    """

    idx_in_brain_state: Optional[int] = None
    action: Optional[Dict[str, Any]] = None
    dom_element_data: Optional[Dict[str, Any]] = None
    valid: Optional[bool] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateAction":
        """
        Generate a sample UpdateAction instance for testing.

        Returns:
            UpdateAction: A sample update action with fake data
        """

        class UpdateActionFactory(ModelFactory[UpdateAction]):
            __model__ = UpdateAction
            __faker__ = faker

            idx_in_brain_state = faker.random_int(min=0, max=50)
            action = generate_action_data(faker)
            dom_element_data = generate_dom_element_data(faker, "div")
            valid = faker.boolean()

        element = UpdateActionFactory.build()

        return element


class ResponseAction(BaseModel):
    """
    Schema for action responses returned by the API.

    Contains all action fields including read-only fields like ID.
    Used for GET operations and when returning action data to clients.

    Attributes:
        id: Unique action identifier
        brain_state_id: Reference to the brain state this action belongs to
        idx_in_brain_state: Index position within the brain state's action sequence
        action: Dictionary containing action details (type, parameters, etc.)
        dom_element_data: Dictionary containing DOM element information
        valid: Whether this action is valid and executable
    """

    id: str
    brain_state_id: str
    idx_in_brain_state: int
    action: Dict[str, Any]
    dom_element_data: Dict[str, Any]
    valid: bool

    @classmethod
    def sample_factory_build(
        cls, id: str = CUID().generate(), brain_state_id: str = CUID().generate()
    ) -> "ResponseAction":
        """
        Generate a sample ResponseAction instance for testing.

        Args:
            id: Action ID to use in the sample
            brain_state_id: Brain state ID that the action belongs to

        Returns:
            ResponseAction: A sample response action with fake data
        """

        class ResponseActionFactory(ModelFactory[ResponseAction]):
            __model__ = ResponseAction
            __faker__ = faker

            idx_in_brain_state = faker.random_int(min=0, max=50)
            action = generate_action_data(faker)
            dom_element_data = generate_dom_element_data(faker, "button")
            valid = faker.boolean()

        element = ResponseActionFactory.build()
        element.id = id
        element.brain_state_id = brain_state_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample actions
    rich_print(CreateAction.sample_factory_build())
    rich_print(UpdateAction.sample_factory_build())
    rich_print(ResponseAction.sample_factory_build())
