from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.project_repo import ProjectRepo
from app.schemas.communication.project import ExtendedResponseProject
from app.schemas.crud.project import (
    CreateProject,
    PaginatedResponseProject,
    ResponseProject,
    UpdateProject,
)

projects_router = APIRouter(prefix="/projects", tags=["Projects"])


@projects_router.post(
    "/",
    response_model=ResponseProject,
    summary="Create Project",
    description="Create a new project with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Project created successfully", ResponseProject),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_project(
    project_data: CreateProject,
    db_session: Session = Depends(get_db),
) -> ResponseProject:
    """
    Create a new project with the specified name and configuration.

    This endpoint creates a new project in the system and returns the created project instance.
    The project will be associated with the current user and can contain documents and test cases.
    """
    try:
        created_project = ProjectRepo.create(db=db_session, project_data=project_data)
        return ResponseProject(
            id=created_project.id,
            created_at=created_project.created_at,
            name=created_project.name,
            default_start_url=created_project.default_start_url,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}",
        )


@projects_router.get(
    "/",
    response_model=PaginatedResponseProject,
    summary="Get All Projects",
    description="Retrieve all projects with pagination and sorting by creation date",
    responses={
        200: create_success_response("Projects retrieved successfully", PaginatedResponseProject),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_all_projects(
    page: int = 1,
    page_size: int = 10,
    sort_order: str = "desc",
    db_session: Session = Depends(get_db),
) -> PaginatedResponseProject:
    """
    Retrieve all projects with pagination and sorting options.

    This endpoint returns a paginated list of all projects in the system,
    sorted by creation date. The most recent projects are returned first by default.

    Args:
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        db_session: Database session
        sort_order: Sort order - "asc" for oldest first, "desc" for newest first

    Returns:
        PaginatedResponseProject: Paginated list of projects with metadata
    """
    try:
        # Validate sort order
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sort_order must be either 'asc' or 'desc'",
            )

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

        # Get projects with sorting and pagination
        projects = ProjectRepo.get_all_with_sorting(
            db=db_session, page=page, page_size=page_size, sort_order=sort_order
        )

        # Get total count for pagination metadata
        total_count = ProjectRepo.count(db=db_session)

        # Convert projects to response models
        project_responses = [
            ResponseProject(
                id=project.id,
                created_at=project.created_at,
                name=project.name,
                default_start_url=project.default_start_url,
            )
            for project in projects
        ]

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedResponseProject(
            items=project_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve projects: {str(e)}",
        )


@projects_router.get(
    "/{project_id:str}",
    response_model=ExtendedResponseProject,
    summary="Get Project by ID",
    description="Retrieve a specific project by its ID with extended information including documents and test cases",
    responses={
        200: create_success_response("Project retrieved successfully", ExtendedResponseProject),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_project_by_id(
    project_id: str,
    db_session: Session = Depends(get_db),
) -> ExtendedResponseProject:
    """
    Retrieve a specific project by its unique identifier.

    This endpoint returns detailed project information including all associated
    documents and test cases for comprehensive project analysis.
    """
    try:
        project = ProjectRepo.get_extended_by_id(db=db_session, project_id=project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found",
            )

        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project: {str(e)}",
        )


@projects_router.put(
    "/{project_id:str}",
    response_model=ResponseProject,
    summary="Update Project",
    description="Update an existing project with new data",
    responses={
        200: create_success_response("Project updated successfully", ResponseProject),
        **COMMON_ERROR_RESPONSES,
    },
)
async def update_project(
    project_id: str,
    project_data: UpdateProject,
    db_session: Session = Depends(get_db),
) -> ResponseProject:
    """
    Update an existing project with new information.

    This endpoint allows you to modify project details such as name and default start URL.
    Only the fields provided in the request will be updated.
    """
    try:
        updated_project = ProjectRepo.update(
            db=db_session, project_id=project_id, project_data=project_data
        )

        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found",
            )

        return ResponseProject(
            id=updated_project.id,
            created_at=updated_project.created_at,
            name=updated_project.name,
            default_start_url=updated_project.default_start_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}",
        )


@projects_router.delete(
    "/{project_id:str}",
    response_model=ResponseProject,
    summary="Delete Project",
    description="Delete a project by its ID",
    responses={
        200: create_success_response("Project deleted successfully", ResponseProject),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_project(
    project_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseProject:
    """
    Delete a project from the system.

    This endpoint permanently removes a project and all its associated data.
    The deleted project information is returned for confirmation.
    """
    try:
        # First get the project to return it after deletion
        project = ProjectRepo.get_by_id(db=db_session, project_id=project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found",
            )

        # Delete the project
        success = ProjectRepo.delete(db=db_session, project_id=project_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete project with id {project_id}",
            )

        return ResponseProject(
            id=project.id,
            created_at=project.created_at,
            name=project.name,
            default_start_url=project.default_start_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}",
        )
