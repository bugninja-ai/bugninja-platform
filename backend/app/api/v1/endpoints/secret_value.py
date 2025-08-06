from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.secret_value_repo import SecretValueRepo
from app.repo.test_case_repo import TestCaseRepo
from app.schemas.crud.secret_value import (
    BulkCreateSecretValueRequest,
    BulkCreateSecretValueResponse,
    BulkUpdateSecretValueRequest,
    BulkUpdateSecretValueResponse,
    CreateSecretValue,
    ResponseSecretValue,
)

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
    secret_value_data: CreateSecretValue,
    db_session: Session = Depends(get_db),
) -> ResponseSecretValue:
    """
    Create a new secret value with the specified name and value.

    This endpoint creates a new secret value in the system and returns the created secret value instance.
    The secret value will be associated with a specific test case and should be encrypted at rest.
    """
    try:
        # Validate that the referenced test case exists
        test_case = TestCaseRepo.get_by_id(
            db=db_session, test_case_id=secret_value_data.test_case_id
        )
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {secret_value_data.test_case_id} not found",
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


@secret_values_router.post(
    "/bulk",
    response_model=BulkCreateSecretValueResponse,
    summary="Bulk Create Secret Values",
    description="Create multiple secret values",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response(
            "Secret values created successfully", BulkCreateSecretValueResponse
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def bulk_create_secret_values(
    request_data: BulkCreateSecretValueRequest,
    db_session: Session = Depends(get_db),
) -> BulkCreateSecretValueResponse:
    """
    Create multiple secret values.

    This endpoint creates multiple secret values in a single operation.
    The endpoint handles partial failures gracefully and returns detailed
    information about successful and failed creations.

    Args:
        request_data: Bulk creation request containing secret values
        db_session: Database session

    Returns:
        BulkCreateSecretValueResponse: Response with created entities and error details
    """
    try:
        # Validate that all secret values reference valid test cases
        test_case_ids = set()
        for secret_value in request_data.secret_values:
            test_case_ids.add(secret_value.test_case_id)

        # Validate all test cases exist and belong to the same project
        test_cases = {}
        project_id = None
        for test_case_id in test_case_ids:
            test_case = TestCaseRepo.get_by_id(db=db_session, test_case_id=test_case_id)
            if not test_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Test case with id {test_case_id} not found",
                )
            test_cases[test_case_id] = test_case

            # Ensure all test cases belong to the same project
            if project_id is None:
                project_id = test_case.project_id
            elif test_case.project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"All secret values must belong to the same project. Expected {project_id}, got {test_case.project_id}",
                )

        # Perform bulk creation
        created_secret_values, failed_creations = SecretValueRepo.bulk_create(
            db=db_session, secret_values_data=request_data.secret_values
        )

        # Convert to response models
        response_secret_values = [
            ResponseSecretValue(
                id=sv.id,
                project_id=sv.project_id,
                created_at=sv.created_at,
                updated_at=sv.updated_at,
                secret_name=sv.secret_name,
                secret_value=sv.secret_value,
            )
            for sv in created_secret_values
        ]

        return BulkCreateSecretValueResponse(
            created_secret_values=response_secret_values,
            total_created=len(created_secret_values),
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
            detail=f"Failed to create secret values: {str(e)}",
        )


@secret_values_router.put(
    "/bulk",
    response_model=BulkUpdateSecretValueResponse,
    summary="Bulk Update Secret Values",
    description="Update multiple secret values",
    responses={
        200: create_success_response(
            "Secret values updated successfully", BulkUpdateSecretValueResponse
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def bulk_update_secret_values(
    request_data: BulkUpdateSecretValueRequest,
    db_session: Session = Depends(get_db),
) -> BulkUpdateSecretValueResponse:
    """
    Update multiple secret values.

    This endpoint updates multiple secret values in a single operation.
    The endpoint handles partial failures gracefully and returns detailed
    information about successful and failed updates.

    Args:
        request_data: Bulk update request containing secret value updates
        db_session: Database session

    Returns:
        BulkUpdateSecretValueResponse: Response with updated entities and error details
    """
    try:
        # Perform bulk update with linking/unlinking capabilities
        (
            updated_secret_values,
            created_secret_values,
            linked_secret_values,
            failed_updates,
            failed_creations,
            failed_links,
            unlinked_count,
        ) = SecretValueRepo.bulk_update(
            db=db_session,
            secret_values_data=request_data.secret_values,
            new_secret_values=request_data.new_secret_values,
            existing_secret_value_ids_to_add=request_data.existing_secret_value_ids_to_add,
            secret_value_ids_to_unlink=request_data.secret_value_ids_to_unlink,
            test_case_id=request_data.test_case_id,
        )

        # Convert to response models
        updated_response_secret_values = [
            ResponseSecretValue(
                id=sv.id,
                project_id=sv.project_id,
                created_at=sv.created_at,
                updated_at=sv.updated_at,
                secret_name=sv.secret_name,
                secret_value=sv.secret_value,
            )
            for sv in updated_secret_values
        ]

        linked_response_secret_values = [
            ResponseSecretValue(
                id=sv.id,
                project_id=sv.project_id,
                created_at=sv.created_at,
                updated_at=sv.updated_at,
                secret_name=sv.secret_name,
                secret_value=sv.secret_value,
            )
            for sv in linked_secret_values
        ]

        # Convert created secrets to response models
        created_response_secret_values = [
            ResponseSecretValue(
                id=sv.id,
                project_id=sv.project_id,
                created_at=sv.created_at,
                updated_at=sv.updated_at,
                secret_name=sv.secret_name,
                secret_value=sv.secret_value,
            )
            for sv in created_secret_values
        ]

        return BulkUpdateSecretValueResponse(
            updated_secret_values=updated_response_secret_values,
            created_secret_values=created_response_secret_values,
            linked_secret_values=linked_response_secret_values,
            total_updated=len(updated_secret_values),
            total_created=len(created_secret_values),
            total_linked=len(linked_secret_values),
            total_unlinked=unlinked_count,
            failed_updates=failed_updates,
            failed_creations=failed_creations,
            failed_links=failed_links,
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
            detail=f"Failed to update secret values: {str(e)}",
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
    page: int = 1,
    page_size: int = 10,
    db_session: Session = Depends(get_db),
) -> List[ResponseSecretValue]:
    """
    Retrieve all secret values for a specific project.

    This endpoint returns a paginated list of all secret values associated with a particular project.
    Use page and page_size parameters for pagination control.
    Note: Secret values should be masked or encrypted in production responses.

    Args:
        project_id: Project identifier
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        db_session: Database session

    Returns:
        List[ResponseSecretValue]: List of secret values
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

        secret_values = SecretValueRepo.get_by_project_id(
            db=db_session, project_id=project_id, skip=skip, limit=page_size
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
        409: {"description": "Conflict - Secret value is still in use"},
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
    If the secret value is still being used by test cases, it will return a 409 Conflict error.
    """
    try:
        # First get the secret value to return it after deletion
        secret_value = SecretValueRepo.get_by_id(db=db_session, secret_value_id=secret_value_id)

        if not secret_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret value with id {secret_value_id} not found",
            )

        # Check if secret value is still being used
        is_in_use, usage_details = SecretValueRepo.check_usage(
            db=db_session, secret_value_id=secret_value_id
        )

        if is_in_use:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete secret value. It is still being used by {usage_details}",
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
