from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.project_repo import ProjectRepo
from app.schemas.communication.project import ExtendedResponseProject
from app.schemas.crud.project import CreateProject, ResponseProject, UpdateProject

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
    project_data: CreateProject = Depends(),
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
    project_data: UpdateProject = Depends(),
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
