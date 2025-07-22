from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.project_repo import ProjectRepo
from app.repo.secret_value_repo import SecretValueRepo
from app.schemas.crud.secret_value import CreateSecretValue, ResponseSecretValue

secret_values_router = APIRouter(prefix="/secret-values", tags=["Secret Values"])


@secret_values_router.post(
    "/",
    response_model=ResponseSecretValue,
    summary="Create Secret Value",
    description="Create a new secret value with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Secret value created successfully", ResponseSecretValue),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_secret_value(
    secret_value_data: CreateSecretValue = Depends(),
    db_session: Session = Depends(get_db),
) -> ResponseSecretValue:
    """
    Create a new secret value with the specified name and value.

    This endpoint creates a new secret value in the system and returns the created secret value instance.
    The secret value will be associated with a specific project and should be encrypted at rest.
    """
    try:
        # Validate that the referenced project exists
        project = ProjectRepo.get_by_id(db=db_session, project_id=secret_value_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {secret_value_data.project_id} not found",
            )

        created_secret_value = SecretValueRepo.create(
            db=db_session, secret_value_data=secret_value_data
        )
        return ResponseSecretValue(
            id=created_secret_value.id,
            project_id=created_secret_value.project_id,
            created_at=created_secret_value.created_at,
            updated_at=created_secret_value.updated_at,
            secret_name=created_secret_value.secret_name,
            secret_value=created_secret_value.secret_value,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create secret value: {str(e)}",
        )


@secret_values_router.get(
    "/{secret_value_id:str}",
    response_model=ResponseSecretValue,
    summary="Get Secret Value by ID",
    description="Retrieve a specific secret value by its ID",
    responses={
        200: create_success_response("Secret value retrieved successfully", ResponseSecretValue),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_secret_value_by_id(
    secret_value_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseSecretValue:
    """
    Retrieve a specific secret value by its unique identifier.

    This endpoint returns detailed secret value information including the secret name and value.
    Note: The secret value should be masked or encrypted in production responses.
    """
    try:
        secret_value = SecretValueRepo.get_by_id(db=db_session, secret_value_id=secret_value_id)

        if not secret_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret value with id {secret_value_id} not found",
            )

        return ResponseSecretValue(
            id=secret_value.id,
            project_id=secret_value.project_id,
            created_at=secret_value.created_at,
            updated_at=secret_value.updated_at,
            secret_name=secret_value.secret_name,
            secret_value=secret_value.secret_value,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve secret value: {str(e)}",
        )


@secret_values_router.get(
    "/project/{project_id:str}",
    response_model=List[ResponseSecretValue],
    summary="Get Secret Values by Project",
    description="Retrieve all secret values for a specific project",
    responses={
        200: create_success_response(
            "Project secret values retrieved successfully", ResponseSecretValue
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_secret_values_by_project(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
) -> List[ResponseSecretValue]:
    """
    Retrieve all secret values for a specific project.

    This endpoint returns a paginated list of all secret values associated with a particular project.
    Use skip and limit parameters for pagination control.
    Note: Secret values should be masked or encrypted in production responses.
    """
    try:
        secret_values = SecretValueRepo.get_by_project_id(
            db=db_session, project_id=project_id, skip=skip, limit=limit
        )
        return [
            ResponseSecretValue(
                id=sv.id,
                project_id=sv.project_id,
                created_at=sv.created_at,
                updated_at=sv.updated_at,
                secret_name=sv.secret_name,
                secret_value=sv.secret_value,
            )
            for sv in secret_values
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project secret values: {str(e)}",
        )


@secret_values_router.delete(
    "/{secret_value_id:str}",
    response_model=ResponseSecretValue,
    summary="Delete Secret Value",
    description="Delete a secret value by its ID",
    responses={
        200: create_success_response("Secret value deleted successfully", ResponseSecretValue),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_secret_value(
    secret_value_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseSecretValue:
    """
    Delete a secret value from the system.

    This endpoint permanently removes a secret value and returns the deleted secret value information.
    """
    try:
        # First get the secret value to return it after deletion
        secret_value = SecretValueRepo.get_by_id(db=db_session, secret_value_id=secret_value_id)

        if not secret_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret value with id {secret_value_id} not found",
            )

        # Delete the secret value
        success = SecretValueRepo.delete(db=db_session, secret_value_id=secret_value_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete secret value with id {secret_value_id}",
            )

        return ResponseSecretValue(
            id=secret_value.id,
            project_id=secret_value.project_id,
            created_at=secret_value.created_at,
            updated_at=secret_value.updated_at,
            secret_name=secret_value.secret_name,
            secret_value=secret_value.secret_value,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete secret value: {str(e)}",
        )
