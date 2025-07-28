from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.browser_config_repo import BrowserConfigRepo
from app.repo.test_case_repo import TestCaseRepo
from app.repo.test_traversal_repo import TestTraversalRepo
from app.schemas.communication.test_traversal import ExtendedResponseTestTraversal
from app.schemas.crud.test_traversal import (
    CreateTestTraversal,
    PaginatedResponseExtendedTestTraversal,
    PaginatedResponseTestTraversal,
    ResponseTestTraversal,
    UpdateTestTraversal,
)

test_traversals_router = APIRouter(prefix="/test-traversals", tags=["Test Traversals"])


@test_traversals_router.post(
    "/",
    response_model=ResponseTestTraversal,
    summary="Create Test Traversal",
    description="Create a new test traversal with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Test traversal created successfully", ResponseTestTraversal),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_test_traversal(
    test_traversal_data: CreateTestTraversal,
    db_session: Session = Depends(get_db),
) -> ResponseTestTraversal:
    """
    Create a new test traversal with the specified settings.

    This endpoint creates a new test traversal in the system and returns the created traversal instance.
    The traversal will be associated with a specific test case and browser configuration.
    """
    try:
        # Validate that the referenced test case exists
        test_case = TestCaseRepo.get_by_id(
            db=db_session, test_case_id=test_traversal_data.test_case_id
        )
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {test_traversal_data.test_case_id} not found",
            )

        # Validate that the referenced browser config exists
        browser_config = BrowserConfigRepo.get_by_id(
            db=db_session, browser_config_id=test_traversal_data.browser_config_id
        )
        if not browser_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Browser configuration with id {test_traversal_data.browser_config_id} not found",
            )

        created_test_traversal = TestTraversalRepo.create(
            db=db_session, test_traversal_data=test_traversal_data
        )
        return ResponseTestTraversal(
            id=created_test_traversal.id,
            test_case_id=created_test_traversal.test_case_id,
            browser_config_id=created_test_traversal.browser_config_id,
            created_at=created_test_traversal.created_at,
            traversal_name=created_test_traversal.traversal_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test traversal: {str(e)}",
        )


@test_traversals_router.get(
    "/",
    response_model=PaginatedResponseExtendedTestTraversal,
    summary="Get All Test Traversals",
    description="Retrieve all test traversals with pagination, sorting, and test case filtering",
    responses={
        200: create_success_response(
            "Test traversals retrieved successfully", PaginatedResponseExtendedTestTraversal
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_all_test_traversals(
    page: int = 1,
    page_size: int = 10,
    sort_order: str = "desc",
    test_case_id: Optional[str] = None,
    db_session: Session = Depends(get_db),
) -> PaginatedResponseExtendedTestTraversal:
    """
    Retrieve all test traversals with pagination, sorting, and test case filtering.

    This endpoint returns a paginated list of extended test traversals in the system,
    sorted by creation date. The most recent test traversals are returned first by default.
    Each test traversal includes associated browser configurations, latest run details, and secret values.
    Optionally filter by test case ID to get only test traversals for a specific test case.

    Args:
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        sort_order: Sort order - "asc" for oldest first, "desc" for newest first (default: "desc")
        test_case_id: Optional test case ID to filter by (default: None - returns all test traversals)
        db_session: Database session

    Returns:
        PaginatedResponseExtendedTestTraversal: Paginated list of extended test traversals with metadata
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

        # Handle test_case_id filtering
        if test_case_id:
            test_case = TestCaseRepo.get_by_id(db=db_session, test_case_id=test_case_id)
            if not test_case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Test case with id {test_case_id} not found",
                )

        # Get extended test traversals with sorting, pagination, and filtering
        extended_test_traversals = TestTraversalRepo.get_all_extended_with_sorting_and_filter(
            db=db_session,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            test_case_id=test_case_id,
        )

        # Get total count for pagination metadata
        total_count = TestTraversalRepo.count_with_filter(db=db_session, test_case_id=test_case_id)

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedResponseExtendedTestTraversal(
            items=extended_test_traversals,
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
            detail=f"Failed to retrieve test traversals: {str(e)}",
        )


@test_traversals_router.get(
    "/{test_traversal_id:str}",
    response_model=ExtendedResponseTestTraversal,
    summary="Get Test Traversal by ID (Extended)",
    description="Retrieve a specific test traversal by its ID with extended details including browser config, latest run, and secret values",
    responses={
        200: create_success_response(
            "Test traversal retrieved successfully", ExtendedResponseTestTraversal
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_test_traversal_by_id(
    test_traversal_id: str,
    db_session: Session = Depends(get_db),
) -> ExtendedResponseTestTraversal:
    """
    Retrieve a specific test traversal by its unique identifier with extended details.

    This endpoint returns comprehensive test traversal information including:
    - Basic traversal details
    - Associated browser configuration
    - Latest test run information
    - Attached secret values
    """
    try:
        extended_test_traversal = TestTraversalRepo.get_extended_by_id(
            db=db_session, test_traversal_id=test_traversal_id
        )

        if not extended_test_traversal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test traversal with id {test_traversal_id} not found",
            )

        return extended_test_traversal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test traversal: {str(e)}",
        )


@test_traversals_router.put(
    "/{test_traversal_id:str}",
    response_model=ResponseTestTraversal,
    summary="Update Test Traversal",
    description="Update an existing test traversal",
    responses={
        200: create_success_response("Test traversal updated successfully", ResponseTestTraversal),
        **COMMON_ERROR_RESPONSES,
    },
)
async def update_test_traversal(
    test_traversal_id: str,
    test_traversal_data: UpdateTestTraversal,
    db_session: Session = Depends(get_db),
) -> ResponseTestTraversal:
    """
    Update an existing test traversal with new data.

    This endpoint allows updating the traversal name and automatically updates the timestamp.
    The relationships to test case and browser config remain unchanged.
    """
    try:
        updated_test_traversal = TestTraversalRepo.update(
            db=db_session,
            test_traversal_id=test_traversal_id,
            test_traversal_data=test_traversal_data,
        )

        if not updated_test_traversal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test traversal with id {test_traversal_id} not found",
            )

        return ResponseTestTraversal(
            id=updated_test_traversal.id,
            test_case_id=updated_test_traversal.test_case_id,
            browser_config_id=updated_test_traversal.browser_config_id,
            created_at=updated_test_traversal.created_at,
            traversal_name=updated_test_traversal.traversal_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test traversal: {str(e)}",
        )


@test_traversals_router.delete(
    "/{test_traversal_id:str}",
    response_model=ResponseTestTraversal,
    summary="Delete Test Traversal",
    description="Delete a test traversal by its ID",
    responses={
        200: create_success_response("Test traversal deleted successfully", ResponseTestTraversal),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_test_traversal(
    test_traversal_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseTestTraversal:
    """
    Delete a test traversal from the system.

    This endpoint permanently removes a test traversal and returns the deleted traversal information.
    """
    try:
        # First get the test traversal to return it after deletion
        test_traversal = TestTraversalRepo.get_by_id(
            db=db_session, test_traversal_id=test_traversal_id
        )

        if not test_traversal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test traversal with id {test_traversal_id} not found",
            )

        # Delete the test traversal
        success = TestTraversalRepo.delete(db=db_session, test_traversal_id=test_traversal_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete test traversal with id {test_traversal_id}",
            )

        return ResponseTestTraversal(
            id=test_traversal.id,
            test_case_id=test_traversal.test_case_id,
            browser_config_id=test_traversal.browser_config_id,
            created_at=test_traversal.created_at,
            traversal_name=test_traversal.traversal_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete test traversal: {str(e)}",
        )
