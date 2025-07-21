"""
Action CRUD Schemas

This module defines Pydantic models for Action entity CRUD operations.
Actions represent specific UI interactions performed by the AI agent during test execution.
"""

from typing import Any, Dict

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateAction(CreationModel):
    """
    Schema for creating a new action.

    Actions represent specific UI interactions performed by the AI agent during test execution.
    Each action is associated with a brain state and contains details about the interaction
    including the action type and DOM element data.

    Attributes:
        id: Unique identifier generated using CUID
        brain_state_id: Reference to the brain state this action belongs to
        idx_in_brain_state: Index position within the brain state's action sequence
        action: Dictionary containing action details (type, parameters, etc.)
        dom_element_data: Dictionary containing DOM element information
        valid: Whether this action is valid and executable
    """

    id: str = Field(default=CUID().generate())
    brain_state_id: str
    idx_in_brain_state: int
    action: Dict[str, Any]
    dom_element_data: Dict[str, Any]
    valid: bool

    @classmethod
    def sample_factory_build(cls, brain_state_id: str = CUID().generate()) -> "CreateAction":
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

            # Generate realistic action data based on traversal JSON structure
            action_types = [
                "done",
                "search_google",
                "go_to_url",
                "go_back",
                "wait",
                "click_element_by_index",
                "input_text",
                "save_pdf",
                "switch_tab",
                "open_tab",
                "close_tab",
                "extract_content",
                "get_ax_tree",
                "scroll_down",
                "scroll_up",
                "send_keys",
                "scroll_to_text",
                "get_dropdown_options",
                "select_dropdown_option",
                "drag_drop",
                "third_party_authentication_wait",
            ]

            action = {action_type: None for action_type in action_types}

            # Set a random action type with realistic data
            selected_action = faker.random_element(
                [
                    {"go_to_url": {"url": f"https://{faker.domain_name()}"}},
                    {"click_element_by_index": {"index": faker.random_int(1, 20), "xpath": None}},
                    {
                        "input_text": {
                            "index": faker.random_int(1, 20),
                            "text": faker.word(),
                            "xpath": None,
                        }
                    },
                    {"done": {"text": faker.sentence(), "success": faker.boolean()}},
                ]
            )

            action.update(selected_action)

            # Generate realistic DOM element data
            dom_element_data = {
                "tag_name": faker.random_element(["input", "button", "a", "div", "span", "form"]),
                "xpath": f"html/body/div[{faker.random_int(1, 5)}]/div/div[{faker.random_int(1, 3)}]/div/div[{faker.random_int(1, 3)}]/div[{faker.random_int(1, 3)}]/form/div[{faker.random_int(1, 3)}]/input",
                "attributes": {
                    "type": faker.random_element(["text", "email", "password", "submit", "button"]),
                    "class": faker.text(max_nb_chars=100),
                    "id": faker.word(),
                    "placeholder": faker.sentence(nb_words=3),
                    "required": "",
                    "value": faker.word() if faker.boolean() else "",
                },
                "is_visible": True,
                "is_interactive": True,
                "is_top_element": True,
                "is_in_viewport": True,
                "shadow_root": False,
                "highlight_index": faker.random_int(1, 20),
                "viewport_coordinates": None,
                "page_coordinates": None,
                "children": [],
                "alternative_relative_xpaths": [
                    f"//{faker.random_element(['input', 'button', 'a'])}[@id='{faker.word()}']",
                    f"//form/div[{faker.random_int(1, 3)}]/input",
                    f"//div[contains(@class, '{faker.word()}')]/input",
                ],
            }

            valid = faker.boolean()

        element = CreateActionFactory.build()
        element.brain_state_id = brain_state_id

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

    idx_in_brain_state: int
    action: Dict[str, Any]
    dom_element_data: Dict[str, Any]
    valid: bool

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

            # Generate realistic action data
            action_types = [
                "done",
                "search_google",
                "go_to_url",
                "go_back",
                "wait",
                "click_element_by_index",
                "input_text",
                "save_pdf",
                "switch_tab",
                "open_tab",
                "close_tab",
                "extract_content",
                "get_ax_tree",
                "scroll_down",
                "scroll_up",
                "send_keys",
                "scroll_to_text",
                "get_dropdown_options",
                "select_dropdown_option",
                "drag_drop",
                "third_party_authentication_wait",
            ]

            action = {action_type: None for action_type in action_types}

            # Set a different action type for variety
            selected_action = faker.random_element(
                [
                    {"scroll_down": {}},
                    {"wait": {"duration": faker.random_int(1000, 5000)}},
                    {"extract_content": {"selector": faker.word()}},
                    {"get_ax_tree": {}},
                ]
            )

            action.update(selected_action)

            # Generate realistic DOM element data
            dom_element_data = {
                "tag_name": faker.random_element(["div", "span", "p", "h1", "h2", "section"]),
                "xpath": f"html/body/div[{faker.random_int(1, 5)}]/div/div[{faker.random_int(1, 3)}]/div/div[{faker.random_int(1, 3)}]/div[{faker.random_int(1, 3)}]/div[{faker.random_int(1, 3)}]",
                "attributes": {
                    "class": faker.text(max_nb_chars=80),
                    "id": faker.word(),
                    "data-testid": faker.word(),
                    "role": faker.random_element(["button", "link", "textbox", "menuitem"]),
                },
                "is_visible": True,
                "is_interactive": faker.boolean(),
                "is_top_element": True,
                "is_in_viewport": True,
                "shadow_root": False,
                "highlight_index": faker.random_int(1, 20),
                "viewport_coordinates": None,
                "page_coordinates": None,
                "children": (
                    [{"text": faker.sentence(nb_words=3), "type": "TEXT_NODE"}]
                    if faker.boolean()
                    else []
                ),
                "alternative_relative_xpaths": [
                    f"//{faker.random_element(['div', 'span', 'p'])}[@class='{faker.word()}']",
                    f"//div[contains(@class, '{faker.word()}')]",
                    f"//*[@data-testid='{faker.word()}']",
                ],
            }

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

            # Generate realistic action data
            action_types = [
                "done",
                "search_google",
                "go_to_url",
                "go_back",
                "wait",
                "click_element_by_index",
                "input_text",
                "save_pdf",
                "switch_tab",
                "open_tab",
                "close_tab",
                "extract_content",
                "get_ax_tree",
                "scroll_down",
                "scroll_up",
                "send_keys",
                "scroll_to_text",
                "get_dropdown_options",
                "select_dropdown_option",
                "drag_drop",
                "third_party_authentication_wait",
            ]

            action = {action_type: None for action_type in action_types}

            # Set a realistic action type
            selected_action = faker.random_element(
                [
                    {"click_element_by_index": {"index": faker.random_int(1, 20), "xpath": None}},
                    {
                        "input_text": {
                            "index": faker.random_int(1, 20),
                            "text": faker.word(),
                            "xpath": None,
                        }
                    },
                    {"go_to_url": {"url": f"https://{faker.domain_name()}"}},
                    {"done": {"text": faker.sentence(), "success": True}},
                ]
            )

            action.update(selected_action)

            # Generate realistic DOM element data
            dom_element_data = {
                "tag_name": faker.random_element(["button", "input", "a", "div", "form"]),
                "xpath": f"html/body/div[{faker.random_int(1, 5)}]/div/div[{faker.random_int(1, 3)}]/div/div[{faker.random_int(1, 3)}]/div[{faker.random_int(1, 3)}]/form/button",
                "attributes": {
                    "type": faker.random_element(["submit", "button", "text", "email"]),
                    "class": faker.text(max_nb_chars=120),
                    "id": faker.word(),
                    "data-umami-event": faker.word(),
                    "href": faker.url() if faker.boolean() else None,
                },
                "is_visible": True,
                "is_interactive": True,
                "is_top_element": True,
                "is_in_viewport": True,
                "shadow_root": False,
                "highlight_index": faker.random_int(1, 20),
                "viewport_coordinates": None,
                "page_coordinates": None,
                "children": (
                    [{"text": faker.sentence(nb_words=2), "type": "TEXT_NODE"}]
                    if faker.boolean()
                    else []
                ),
                "alternative_relative_xpaths": [
                    f"//{faker.random_element(['button', 'input', 'a'])}[@id='{faker.word()}']",
                    f"//form/button",
                    f"//button[text()='{faker.word()}']",
                    f"//div[contains(@class, '{faker.word()}')]/button",
                ],
            }

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
