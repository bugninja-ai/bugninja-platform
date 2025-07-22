"""
Shared utilities for API endpoints.

This module contains common functions and constants used across multiple endpoint files
to reduce boilerplate and ensure consistency in API responses.
"""

from typing import Any, Dict, Optional, Union

# Common response definitions to reduce boilerplate
COMMON_ERROR_RESPONSES: Dict[Union[int, str], Dict[str, Any]] = {
    404: {
        "description": "Resource not found",
        "content": {
            "application/json": {
                "example": {"detail": "Resource with id clx1234567890abcdef not found"}
            }
        },
    },
    500: {
        "description": "Internal server error",
        "content": {"application/json": {"example": {"detail": "Database connection error"}}},
    },
}


def create_success_response(description: str, example_model: Any) -> Dict[str, Any]:
    """
    Create a standardized success response with dynamic example.

    Args:
        description: Description of the successful operation
        example_model: Pydantic model with sample_factory_build method

    Returns:
        Dict containing the standardized success response structure
    """
    return {
        "description": description,
        "content": {
            "application/json": {"example": example_model.sample_factory_build().model_dump()}
        },
    }


def create_error_response(
    status_code: int, description: str, detail: str
) -> Dict[int, Dict[str, Any]]:
    """
    Create a standardized error response.

    Args:
        status_code: HTTP status code for the error
        description: Description of the error
        detail: Detailed error message

    Returns:
        Dict containing the standardized error response structure
    """
    return {
        status_code: {
            "description": description,
            "content": {"application/json": {"example": {"detail": detail}}},
        }
    }


def create_custom_error_responses(
    resource_name: str, additional_errors: Optional[Dict[Union[int, str], Dict[str, Any]]] = None
) -> Dict[Union[int, str], Dict[str, Any]]:
    """
    Create custom error responses for a specific resource.

    Args:
        resource_name: Name of the resource (e.g., "Project", "Test Case")
        additional_errors: Additional error responses to include

    Returns:
        Dict containing custom error responses for the resource
    """
    custom_errors: Dict[Union[int, str], Dict[str, Any]] = {
        404: {
            "description": f"{resource_name} not found",
            "content": {
                "application/json": {
                    "example": {"detail": f"{resource_name} with id clx1234567890abcdef not found"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {"example": {"detail": "Database connection error"}}},
        },
    }

    if additional_errors:
        custom_errors.update(additional_errors)

    return custom_errors
