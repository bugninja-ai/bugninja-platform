from typing import List

from fastapi import APIRouter

from app.api.v1.endpoints.utils import create_success_response
from app.schemas.crud.constants import BROWSER_TYPES

browser_types_router = APIRouter(prefix="/browser-types", tags=["Browser Types"])


@browser_types_router.get(
    "/",
    response_model=List[str],
    summary="Get Available Browser Types",
    description="Retrieve all available browser types based on Playwright configuration",
)
async def get_browser_types() -> List[str]:
    """
    Retrieve all available browser types.

    This endpoint returns a list of all supported browser types that can be used
    for browser configurations. These types are based on the Playwright configuration
    and include both desktop and mobile browsers.

    Returns:
        List[str]: List of available browser types in Title Case
    """
    return BROWSER_TYPES
