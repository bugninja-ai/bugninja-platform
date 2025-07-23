from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.document_repo import DocumentRepo
from app.repo.project_repo import ProjectRepo
from app.repo.test_case_repo import TestCaseRepo
from app.schemas.communication.test_case import ExtendedResponseTestcase
from app.schemas.crud.test_case import (
    CreateTestCase,
    CreateTestCaseResponse,
    PaginatedResponseExtendedTestCase,
    PaginatedResponseTestCase,
    ResponseTestCase,
    UpdateTestCase,
)

test_cases_router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


@test_cases_router.post(
    "/",
    response_model=CreateTestCaseResponse,
    summary="Create Test Case with Dependencies",
    description="Create a new test case with browser configs, secret values, and test traversals",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Test case created successfully", CreateTestCaseResponse),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_test_case_with_dependencies(
    test_case_data: CreateTestCase,
    db_session: Session = Depends(get_db),
) -> CreateTestCaseResponse:
    """
    Create a new test case with all its dependencies.

    This endpoint creates a new test case along with:
    - New browser configurations (if provided)
    - Association with existing browser configurations (if provided)
    - New secret values (if provided)
    - Association with existing secret values (if provided)
    - Test traversals for each browser configuration
    - All secret values associated with each test traversal

    The endpoint validates all dependencies and ensures they belong to the same project.
    """
    try:
        # Use the enhanced creation method that handles all dependencies
        result = TestCaseRepo.create_with_dependencies(db=db_session, test_case_data=test_case_data)
        return result
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
            detail=f"Failed to create test case: {str(e)}",
        )


@test_cases_router.post(
    "/simple",
    response_model=ResponseTestCase,
    summary="Create Simple Test Case",
    description="Create a new test case without dependencies (backward compatibility)",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Test case created successfully", ResponseTestCase),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_simple_test_case(
    test_case_data: CreateTestCase,
    db_session: Session = Depends(get_db),
) -> ResponseTestCase:
    """
    Create a new test case without dependencies (simple creation).

    This endpoint creates a new test case in the system and returns the created test case instance.
    The test case will be associated with a specific project and optionally with a document.
    This endpoint is provided for backward compatibility.
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
    "/",
    response_model=PaginatedResponseExtendedTestCase,
    summary="Get All Test Cases",
    description="Retrieve all test cases with pagination, sorting, and optional project filtering",
    responses={
        200: create_success_response(
            "Test cases retrieved successfully", PaginatedResponseExtendedTestCase
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_all_test_cases(
    page: int = 1,
    page_size: int = 10,
    sort_order: str = "desc",
    project_id: Optional[str] = None,
    db_session: Session = Depends(get_db),
) -> PaginatedResponseExtendedTestCase:
    """
    Retrieve all test cases with pagination, sorting, and optional project filtering.

    This endpoint returns a paginated list of extended test cases in the system,
    sorted by creation date. The most recent test cases are returned first by default.
    Each test case includes associated documents and browser configurations.
    Optionally filter by project ID to get only test cases for a specific project.

    Args:
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        sort_order: Sort order - "asc" for oldest first, "desc" for newest first (default: "desc")
        project_id: Optional project ID to filter by (default: None - returns all test cases)
        db_session: Database session

    Returns:
        PaginatedResponseExtendedTestCase: Paginated list of extended test cases with metadata
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

        # Validate project_id if provided
        if project_id:
            project = ProjectRepo.get_by_id(db=db_session, project_id=project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with id {project_id} not found",
                )

        # Get extended test cases with sorting, pagination, and filtering
        extended_test_cases = TestCaseRepo.get_all_extended_with_sorting_and_filter(
            db=db_session,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            project_id=project_id,
        )

        # Get total count for pagination metadata
        total_count = TestCaseRepo.count_with_filter(db=db_session, project_id=project_id)

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedResponseExtendedTestCase(
            items=extended_test_cases,
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
            detail=f"Failed to retrieve test cases: {str(e)}",
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
    test_case_data: UpdateTestCase,
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
