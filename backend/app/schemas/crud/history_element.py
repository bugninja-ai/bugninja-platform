"""
HistoryElement CRUD Schemas

This module defines Pydantic models for HistoryElement entity CRUD operations.
History elements track individual actions and their outcomes during test execution.
"""

from datetime import datetime
from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.db.history_element import HistoryElementState
from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateHistoryElement(CreationModel):
    """
    Schema for creating a new history element.

    History elements track individual actions and their outcomes during test execution.
    Each history element represents a single action taken by the AI agent during
    a test run, including timing, results, and visual evidence.

    Attributes:
        test_run_id: Reference to the test run this history element belongs to
        action_id: Reference to the specific action that was executed
        history_element_state: State of the action (PASSED or FAILED)
        screenshot: URL or path to the screenshot taken during the action
    """

    test_run_id: str
    action_id: str
    history_element_state: HistoryElementState
    screenshot: str

    @classmethod
    def sample_factory_build(
        cls, test_run_id: str = CUID().generate(), action_id: str = CUID().generate()
    ) -> "CreateHistoryElement":
        """
        Generate a sample CreateHistoryElement instance for testing.

        Args:
            test_run_id: Test run ID that the history element belongs to
            action_id: Action ID that was executed

        Returns:
            CreateHistoryElement: A sample history element with fake data
        """

        class CreateHistoryElementFactory(ModelFactory[CreateHistoryElement]):
            __model__ = CreateHistoryElement
            __faker__ = faker

            history_element_state = faker.random_element(
                [HistoryElementState.PASSED, HistoryElementState.FAILED]
            )
            screenshot = faker.image_url()

        element = CreateHistoryElementFactory.build()
        element.test_run_id = test_run_id
        element.action_id = action_id

        return element


class UpdateHistoryElement(UpdateModel):
    """
    Schema for updating an existing history element.

    Allows updating the action timing, state, and screenshot.
    The relationships to test run and action remain unchanged.

    Attributes:
        action_started_at: Updated timestamp when the action started
        action_finished_at: Updated timestamp when the action finished
        history_element_state: Updated state of the action
        screenshot: Updated URL or path to the screenshot
    """

    action_started_at: Optional[datetime] = None
    action_finished_at: Optional[datetime] = None
    history_element_state: Optional[HistoryElementState] = None
    screenshot: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateHistoryElement":
        """
        Generate a sample UpdateHistoryElement instance for testing.

        Returns:
            UpdateHistoryElement: A sample update history element with fake data
        """

        class UpdateHistoryElementFactory(ModelFactory[UpdateHistoryElement]):
            __model__ = UpdateHistoryElement
            __faker__ = faker

            action_started_at = faker.date_time()
            action_finished_at = faker.date_time()
            history_element_state = faker.random_element(
                [HistoryElementState.PASSED, HistoryElementState.FAILED]
            )
            screenshot = faker.image_url()

        element = UpdateHistoryElementFactory.build()

        return element


class ResponseHistoryElement(BaseModel):
    """
    Schema for history element responses returned by the API.

    Contains all history element fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning history element data to clients.

    Attributes:
        id: Unique history element identifier
        test_run_id: Reference to the test run this history element belongs to
        action_id: Reference to the specific action that was executed
        action_started_at: Timestamp when the action started
        action_finished_at: Timestamp when the action finished
        history_element_state: State of the action (PASSED or FAILED)
        screenshot: URL or path to the screenshot taken during the action
    """

    id: str
    test_run_id: str
    action_id: str
    action_started_at: datetime
    action_finished_at: datetime
    history_element_state: HistoryElementState
    screenshot: str

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        test_run_id: str = CUID().generate(),
        action_id: str = CUID().generate(),
    ) -> "ResponseHistoryElement":
        """
        Generate a sample ResponseHistoryElement instance for testing.

        Args:
            id: History element ID to use in the sample
            test_run_id: Test run ID that the history element belongs to
            action_id: Action ID that was executed

        Returns:
            ResponseHistoryElement: A sample response history element with fake data
        """

        class ResponseHistoryElementFactory(ModelFactory[ResponseHistoryElement]):
            __model__ = ResponseHistoryElement
            __faker__ = faker

            action_started_at = faker.date_time()
            action_finished_at = faker.date_time()
            history_element_state = faker.random_element(
                [HistoryElementState.PASSED, HistoryElementState.FAILED]
            )
            screenshot = faker.image_url()

        element = ResponseHistoryElementFactory.build()
        element.id = id
        element.test_run_id = test_run_id
        element.action_id = action_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample history elements
    rich_print(CreateHistoryElement.sample_factory_build())
    rich_print(UpdateHistoryElement.sample_factory_build())
    rich_print(ResponseHistoryElement.sample_factory_build())
