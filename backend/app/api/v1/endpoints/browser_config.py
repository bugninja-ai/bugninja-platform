from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.browser_config_repo import BrowserConfigRepo
from app.repo.project_repo import ProjectRepo
from app.schemas.crud.browser_config import CreateBrowserConfig, ResponseBrowserConfig

browser_configs_router = APIRouter(prefix="/browser-configs", tags=["Browser Configurations"])


@browser_configs_router.post(
    "/",
    response_model=ResponseBrowserConfig,
    summary="Create Browser Configuration",
    description="Create a new browser configuration with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response(
            "Browser configuration created successfully", ResponseBrowserConfig
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_browser_config(
    browser_config_data: CreateBrowserConfig,
    db_session: Session = Depends(get_db),
) -> ResponseBrowserConfig:
    """
    Create a new browser configuration with the specified settings.

    This endpoint creates a new browser configuration in the system and returns the created configuration instance.
    The configuration will be associated with a specific project and can contain browser-specific settings.
    """
    try:
        # Validate that the referenced project exists
        project = ProjectRepo.get_by_id(db=db_session, project_id=browser_config_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {browser_config_data.project_id} not found",
            )

        created_browser_config = BrowserConfigRepo.create(
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
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
) -> List[ResponseBrowserConfig]:
    """
    Retrieve all browser configurations for a specific project.

    This endpoint returns a paginated list of all browser configurations associated with a particular project.
    Use skip and limit parameters for pagination control.
    """
    try:
        browser_configs = BrowserConfigRepo.get_by_project_id(
            db=db_session, project_id=project_id, skip=skip, limit=limit
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
