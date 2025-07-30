from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.browser_config_repo import BrowserConfigRepo
from app.repo.test_case_repo import TestCaseRepo
from app.schemas.crud.browser_config import (
    BulkCreateBrowserConfigRequest,
    BulkCreateBrowserConfigResponse,
    BulkUpdateBrowserConfigRequest,
    BulkUpdateBrowserConfigResponse,
    CreateBrowserConfig,
    ResponseBrowserConfig,
)

browser_configs_router = APIRouter(prefix="/browser-configs", tags=["Browser Configurations"])


@browser_configs_router.post(
    "/",
    response_model=ResponseBrowserConfig,
    summary="Create Browser Configuration and Test Traversal",
    description="Create a new browser configuration and automatically create a test traversal using a specific test case",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response(
            "Browser configuration and test traversal created successfully", ResponseBrowserConfig
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_browser_config_and_traversal(
    browser_config_data: CreateBrowserConfig,
    db_session: Session = Depends(get_db),
) -> ResponseBrowserConfig:
    """
    Create a new browser configuration and automatically create a test traversal.

    This endpoint creates a new browser configuration and automatically creates a test traversal
    using the specified test case. The test case ID is provided in the browser_config_data.
    The test traversal will be named with the pattern: "Traversal - {test_case_name} ({browser_type})"
    """
    try:
        # Validate that the referenced test case exists
        test_case = TestCaseRepo.get_by_id(
            db=db_session, test_case_id=browser_config_data.test_case_id
        )
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {browser_config_data.test_case_id} not found",
            )

        created_browser_config = BrowserConfigRepo.create_with_traversal(
            db=db_session, browser_config_data=browser_config_data
        )
        return ResponseBrowserConfig(
            id=created_browser_config.id,
            project_id=created_browser_config.project_id,
            created_at=created_browser_config.created_at,
            updated_at=created_browser_config.updated_at,
            browser_config=created_browser_config.browser_config,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create browser configuration: {str(e)}",
        )


@browser_configs_router.post(
    "/bulk",
    response_model=BulkCreateBrowserConfigResponse,
    summary="Bulk Create Browser Configurations",
    description="Create multiple browser configurations with test traversals",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response(
            "Browser configurations created successfully", BulkCreateBrowserConfigResponse
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def bulk_create_browser_configs(
    request_data: BulkCreateBrowserConfigRequest,
    db_session: Session = Depends(get_db),
) -> BulkCreateBrowserConfigResponse:
    """
    Create multiple browser configurations with test traversals.

    This endpoint creates multiple browser configurations and automatically
    creates test traversals for each one using the test case ID specified
    in each browser config. The endpoint handles partial failures gracefully
    and returns detailed information about successful and failed creations.

    Args:
        request_data: Bulk creation request containing browser configs
        db_session: Database session

    Returns:
        BulkCreateBrowserConfigResponse: Response with created entities and error details
    """
    try:
        # Perform bulk creation
        created_browser_configs, failed_creations = BrowserConfigRepo.bulk_create_with_traversals(
            db=db_session,
            browser_configs_data=request_data.browser_configs,
        )

        # Convert to response models
        response_browser_configs = [
            ResponseBrowserConfig(
                id=bc.id,
                project_id=bc.project_id,
                created_at=bc.created_at,
                updated_at=bc.updated_at,
                browser_config=bc.browser_config,
            )
            for bc in created_browser_configs
        ]

        return BulkCreateBrowserConfigResponse(
            created_browser_configs=response_browser_configs,
            total_created=len(created_browser_configs),
            failed_creations=failed_creations,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create browser configurations: {str(e)}",
        )


@browser_configs_router.put(
    "/bulk",
    response_model=BulkUpdateBrowserConfigResponse,
    summary="Bulk Update Browser Configurations",
    description="Update multiple browser configurations",
    responses={
        200: create_success_response(
            "Browser configurations updated successfully", BulkUpdateBrowserConfigResponse
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def bulk_update_browser_configs(
    request_data: BulkUpdateBrowserConfigRequest,
    db_session: Session = Depends(get_db),
) -> BulkUpdateBrowserConfigResponse:
    """
    Update multiple browser configurations.

    This endpoint updates multiple browser configurations in a single operation.
    The endpoint handles partial failures gracefully and returns detailed
    information about successful and failed updates.

    Args:
        request_data: Bulk update request containing browser config updates
        db_session: Database session

    Returns:
        BulkUpdateBrowserConfigResponse: Response with updated entities and error details
    """
    try:
        # Perform bulk update
        updated_browser_configs, failed_updates = BrowserConfigRepo.bulk_update(
            db=db_session,
            browser_configs_data=request_data.browser_configs,
        )

        # Convert to response models
        response_browser_configs = [
            ResponseBrowserConfig(
                id=bc.id,
                project_id=bc.project_id,
                created_at=bc.created_at,
                updated_at=bc.updated_at,
                browser_config=bc.browser_config,
            )
            for bc in updated_browser_configs
        ]

        return BulkUpdateBrowserConfigResponse(
            updated_browser_configs=response_browser_configs,
            total_updated=len(updated_browser_configs),
            failed_updates=failed_updates,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update browser configurations: {str(e)}",
        )


@browser_configs_router.get(
    "/{browser_config_id:str}",
    response_model=ResponseBrowserConfig,
    summary="Get Browser Configuration by ID",
    description="Retrieve a specific browser configuration by its ID",
    responses={
        200: create_success_response(
            "Browser configuration retrieved successfully", ResponseBrowserConfig
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_browser_config_by_id(
    browser_config_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseBrowserConfig:
    """
    Retrieve a specific browser configuration by its unique identifier.

    This endpoint returns detailed browser configuration information including all browser-specific settings.
    """
    try:
        browser_config = BrowserConfigRepo.get_by_id(
            db=db_session, browser_config_id=browser_config_id
        )

        if not browser_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Browser configuration with id {browser_config_id} not found",
            )

        return ResponseBrowserConfig(
            id=browser_config.id,
            project_id=browser_config.project_id,
            created_at=browser_config.created_at,
            updated_at=browser_config.updated_at,
            browser_config=browser_config.browser_config,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve browser configuration: {str(e)}",
        )


@browser_configs_router.get(
    "/project/{project_id:str}",
    response_model=List[ResponseBrowserConfig],
    summary="Get Browser Configurations by Project",
    description="Retrieve all browser configurations for a specific project",
    responses={
        200: create_success_response(
            "Project browser configurations retrieved successfully", ResponseBrowserConfig
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_browser_configs_by_project(
    project_id: str,
    page: int = 1,
    page_size: int = 10,
    db_session: Session = Depends(get_db),
) -> List[ResponseBrowserConfig]:
    """
    Retrieve all browser configurations for a specific project.

    This endpoint returns a paginated list of all browser configurations associated with a particular project.
    Use page and page_size parameters for pagination control.

    Args:
        project_id: Project identifier
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        db_session: Database session

    Returns:
        List[ResponseBrowserConfig]: List of browser configurations
    """
    try:
        # Validate page_size
        if page_size <= 0 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="page_size must be between 1 and 100",
            )

        # Validate page
        if page <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="page must be 1 or greater",
            )

        # Calculate skip from page and page_size
        skip = (page - 1) * page_size

        browser_configs = BrowserConfigRepo.get_by_project_id(
            db=db_session, project_id=project_id, skip=skip, limit=page_size
        )
        return [
            ResponseBrowserConfig(
                id=bc.id,
                project_id=bc.project_id,
                created_at=bc.created_at,
                updated_at=bc.updated_at,
                browser_config=bc.browser_config,
            )
            for bc in browser_configs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project browser configurations: {str(e)}",
        )


@browser_configs_router.delete(
    "/{browser_config_id:str}",
    response_model=ResponseBrowserConfig,
    summary="Delete Browser Configuration",
    description="Delete a browser configuration by its ID",
    responses={
        200: create_success_response(
            "Browser configuration deleted successfully", ResponseBrowserConfig
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_browser_config(
    browser_config_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseBrowserConfig:
    """
    Delete a browser configuration from the system.

    This endpoint permanently removes a browser configuration and returns the deleted configuration information.
    """
    try:
        # First get the browser config to return it after deletion
        browser_config = BrowserConfigRepo.get_by_id(
            db=db_session, browser_config_id=browser_config_id
        )

        if not browser_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Browser configuration with id {browser_config_id} not found",
            )

        # Delete the browser config
        success = BrowserConfigRepo.delete(db=db_session, browser_config_id=browser_config_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete browser configuration with id {browser_config_id}",
            )

        return ResponseBrowserConfig(
            id=browser_config.id,
            project_id=browser_config.project_id,
            created_at=browser_config.created_at,
            updated_at=browser_config.updated_at,
            browser_config=browser_config.browser_config,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete browser configuration: {str(e)}",
        )
