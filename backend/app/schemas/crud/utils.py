"""
Utility functions for CRUD schema data generation.
"""

from typing import Any, Dict

from faker import Faker

from app.schemas.crud.constants import (
    ACTION_DATA_TEMPLATES,
    ACTION_TYPES,
    BROWSER_CONFIG_TEMPLATES,
    COLOR_SCHEMES,
    DOM_ELEMENT_TYPES,
    DOM_TAG_NAMES,
)


def generate_action_data(faker: Faker) -> Dict[str, Any]:
    """
    Generate realistic action data using constants.

    Args:
        faker: Faker instance for data generation

    Returns:
        Dict containing action data with one action type set
    """
    # Create action dict with all types set to None
    action: Dict[str, Any] = {action_type: None for action_type in ACTION_TYPES}

    # Select and set one action type with realistic data
    selected_action: Dict[str, Any] = faker.random_element(ACTION_DATA_TEMPLATES)
    action_key = list(selected_action.keys())[0]
    action[action_key] = selected_action[action_key]

    return action


def generate_dom_element_data(faker: Faker, context: str = "input") -> Dict[str, Any]:
    """
    Generate realistic DOM element data.

    Args:
        faker: Faker instance for data generation
        context: Context for element type ("input", "button", "form", etc.)

    Returns:
        Dict containing DOM element data
    """
    tag_name = faker.random_element(DOM_TAG_NAMES)

    # Generate appropriate attributes based on tag
    attributes: Dict[str, Any] = {}
    if tag_name == "input":
        attributes = {
            "type": faker.random_element(DOM_ELEMENT_TYPES["input"]),
            "class": faker.text(max_nb_chars=100),
            "id": faker.word(),
            "placeholder": faker.sentence(nb_words=3),
            "required": "",
            "value": faker.word() if faker.boolean() else "",
        }
    elif tag_name == "button":
        attributes = {
            "type": faker.random_element(DOM_ELEMENT_TYPES["button"]),
            "class": faker.text(max_nb_chars=120),
            "id": faker.word(),
            "data-umami-event": faker.word(),
        }
    else:
        attributes = {
            "class": faker.text(max_nb_chars=80),
            "id": faker.word(),
            "data-testid": faker.word(),
            "role": faker.random_element(["button", "link", "textbox", "menuitem"]),
        }

    # Add href for anchor tags
    if tag_name == "a":
        attributes["href"] = faker.url() if faker.boolean() else None

    return {
        "tag_name": tag_name,
        "xpath": f"html/body/div[{faker.random_int(1, 5)}]/div/div[{faker.random_int(1, 3)}]/div/div[{faker.random_int(1, 3)}]/div[{faker.random_int(1, 3)}]/form/div[{faker.random_int(1, 3)}]/input",
        "attributes": attributes,
        "is_visible": True,
        "is_interactive": True,
        "is_top_element": True,
        "is_in_viewport": True,
        "shadow_root": False,
        "highlight_index": faker.random_int(1, 20),
        "viewport_coordinates": None,
        "page_coordinates": None,
        "children": (
            [{"text": faker.sentence(nb_words=3), "type": "TEXT_NODE"}] if faker.boolean() else []
        ),
        "alternative_relative_xpaths": [
            f"//{faker.random_element(['input', 'button', 'a'])}[@id='{faker.word()}']",
            f"//form/div[{faker.random_int(1, 3)}]/input",
            f"//div[contains(@class, '{faker.word()}')]/input",
        ],
    }


def generate_browser_config_data(faker: Faker, template_type: str = "default") -> Dict[str, Any]:
    """
    Generate realistic browser configuration data using constants.

    Args:
        faker: Faker instance for data generation
        template_type: Type of browser config template ("default", "alternative", "response")

    Returns:
        Dict containing browser configuration data
    """
    template: Dict[str, Any] = BROWSER_CONFIG_TEMPLATES[template_type].copy()

    # Fill in dynamic values
    template["user_agent"] = faker.user_agent()
    template["color_scheme"] = faker.random_element(COLOR_SCHEMES)

    # Generate allowed domains
    if template_type == "response":
        # Use predefined domains for response template
        template["allowed_domains"] = ["example.com", "test.org", "demo.net"]
    else:
        # Generate random domains
        template["allowed_domains"] = [faker.domain_name() for _ in range(faker.random_int(1, 5))]

    # Handle headers for alternative template
    if template_type == "alternative" and "headers" in template:
        template["headers"]["User-Agent"] = faker.user_agent()

    return template
