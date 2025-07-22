from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.document_repo import DocumentRepo
from app.repo.project_repo import ProjectRepo
from app.repo.test_case_repo import TestCaseRepo
from app.schemas.communication.test_case import ExtendedResponseTestcase
from app.schemas.crud.test_case import CreateTestCase, ResponseTestCase, UpdateTestCase

test_cases_router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


@test_cases_router.post(
    "/",
    response_model=ResponseTestCase,
    summary="Create Test Case",
    description="Create a new test case with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Test case created successfully", ResponseTestCase),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_test_case(
    test_case_data: CreateTestCase = Depends(),
    db_session: Session = Depends(get_db),
) -> ResponseTestCase:
    """
    Create a new test case with the specified settings.

    This endpoint creates a new test case in the system and returns the created test case instance.
    The test case will be associated with a specific project and optionally with a document.
    """
    try:
        # Validate that the referenced project exists
        project = ProjectRepo.get_by_id(db=db_session, project_id=test_case_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {test_case_data.project_id} not found",
            )

        # Validate that the referenced document exists (if provided)
        if test_case_data.document_id:
            document = DocumentRepo.get_by_id(db=db_session, document_id=test_case_data.document_id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document with id {test_case_data.document_id} not found",
                )

        created_test_case = TestCaseRepo.create(db=db_session, test_case_data=test_case_data)
        return ResponseTestCase(
            id=created_test_case.id,
            project_id=created_test_case.project_id,
            document_id=created_test_case.document_id,
            created_at=created_test_case.created_at,
            updated_at=created_test_case.updated_at,
            test_name=created_test_case.test_name,
            test_description=created_test_case.test_description,
            test_goal=created_test_case.test_goal,
            extra_rules=created_test_case.extra_rules,
            url_route=created_test_case.url_route,
            allowed_domains=created_test_case.allowed_domains,
            priority=created_test_case.priority,
            category=created_test_case.category,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test case: {str(e)}",
        )


@test_cases_router.get(
    "/{test_case_id:str}",
    response_model=ExtendedResponseTestcase,
    summary="Get Test Case by ID (Extended)",
    description="Retrieve a specific test case by its ID with extended details including document information",
    responses={
        200: create_success_response("Test case retrieved successfully", ExtendedResponseTestcase),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_test_case_by_id(
    test_case_id: str,
    db_session: Session = Depends(get_db),
) -> ExtendedResponseTestcase:
    """
    Retrieve a specific test case by its unique identifier with extended details.

    This endpoint returns comprehensive test case information including:
    - Basic test case details
    - Associated document information (if any)
    - All test configuration and validation rules
    """
    try:
        extended_test_case = TestCaseRepo.get_extended_by_id(
            db=db_session, test_case_id=test_case_id
        )

        if not extended_test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {test_case_id} not found",
            )

        return extended_test_case
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test case: {str(e)}",
        )


@test_cases_router.put(
    "/{test_case_id:str}",
    response_model=ResponseTestCase,
    summary="Update Test Case",
    description="Update an existing test case",
    responses={
        200: create_success_response("Test case updated successfully", ResponseTestCase),
        **COMMON_ERROR_RESPONSES,
    },
)
async def update_test_case(
    test_case_id: str,
    test_case_data: UpdateTestCase = Depends(),
    db_session: Session = Depends(get_db),
) -> ResponseTestCase:
    """
    Update an existing test case with new data.

    This endpoint allows updating all test case fields except ID and relationships.
    The timestamp is automatically updated when modified.
    """
    try:
        updated_test_case = TestCaseRepo.update(
            db=db_session, test_case_id=test_case_id, test_case_data=test_case_data
        )

        if not updated_test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {test_case_id} not found",
            )

        return ResponseTestCase(
            id=updated_test_case.id,
            project_id=updated_test_case.project_id,
            document_id=updated_test_case.document_id,
            created_at=updated_test_case.created_at,
            updated_at=updated_test_case.updated_at,
            test_name=updated_test_case.test_name,
            test_description=updated_test_case.test_description,
            test_goal=updated_test_case.test_goal,
            extra_rules=updated_test_case.extra_rules,
            url_route=updated_test_case.url_route,
            allowed_domains=updated_test_case.allowed_domains,
            priority=updated_test_case.priority,
            category=updated_test_case.category,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test case: {str(e)}",
        )


@test_cases_router.delete(
    "/{test_case_id:str}",
    response_model=ResponseTestCase,
    summary="Delete Test Case",
    description="Delete a test case by its ID",
    responses={
        200: create_success_response("Test case deleted successfully", ResponseTestCase),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_test_case(
    test_case_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseTestCase:
    """
    Delete a test case from the system.

    This endpoint permanently removes a test case and returns the deleted test case information.
    """
    try:
        # First get the test case to return it after deletion
        test_case = TestCaseRepo.get_by_id(db=db_session, test_case_id=test_case_id)

        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {test_case_id} not found",
            )

        # Delete the test case
        success = TestCaseRepo.delete(db=db_session, test_case_id=test_case_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete test case with id {test_case_id}",
            )

        return ResponseTestCase(
            id=test_case.id,
            project_id=test_case.project_id,
            document_id=test_case.document_id,
            created_at=test_case.created_at,
            updated_at=test_case.updated_at,
            test_name=test_case.test_name,
            test_description=test_case.test_description,
            test_goal=test_case.test_goal,
            extra_rules=test_case.extra_rules,
            url_route=test_case.url_route,
            allowed_domains=test_case.allowed_domains,
            priority=test_case.priority,
            category=test_case.category,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete test case: {str(e)}",
        )
