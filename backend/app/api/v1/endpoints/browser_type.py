from typing import Dict, List, Any

from fastapi import APIRouter

from app.api.v1.endpoints.utils import create_success_response
from app.schemas.crud.constants import BROWSER_CHANNELS, USER_AGENTS, VIEWPORT_SIZES

browser_types_router = APIRouter(prefix="/browser-types", tags=["Browser Types"])


@browser_types_router.get(
    "/",
    response_model=Dict[str, Any],
    summary="Get Browser Configuration Options",
    description="Retrieve all available browser configuration options including channels, user agents, and viewport sizes",
)
async def get_browser_config_options() -> Dict[str, Any]:
    """
    Retrieve all available browser configuration options.

    This endpoint returns all the predefined options for browser configurations
    including browser channels, user agents, and viewport sizes. These values
    are the only allowed options for browser configurations.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - browser_channels: List of available browser channels
            - user_agents: List of predefined user agent strings
            - viewport_sizes: List of viewport dimension objects
    """
    return {
        "browser_channels": BROWSER_CHANNELS,
        "user_agents": USER_AGENTS,
        "viewport_sizes": VIEWPORT_SIZES,
    }
