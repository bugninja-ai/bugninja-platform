from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.test_run_repo import TestRunRepo
from app.repo.test_traversal_repo import TestTraversalRepo
from app.schemas.communication.test_run import (
    ExtendedResponseTestRun,
    PaginatedResponseExtendedTestRun,
)
from app.schemas.crud.test_run import (
    CreateTestRun,
    ResponseTestRun,
    UpdateTestRun,
)

test_runs_router = APIRouter(prefix="/test-runs", tags=["Test Runs"])


@test_runs_router.post(
    "/",
    response_model=ResponseTestRun,
    summary="Create Test Run",
    description="Create a new test run with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Test run created successfully", ResponseTestRun),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_test_run(
    test_run_data: CreateTestRun,
    db_session: Session = Depends(get_db),
) -> ResponseTestRun:
    """
    Create a new test run with the specified settings.

    This endpoint creates a new test run in the system and returns the created test run instance.
    The test run will be associated with a specific test traversal and browser configuration.
    """
    try:
        # Validate that the referenced test traversal exists
        test_traversal = TestTraversalRepo.get_by_id(
            db=db_session, test_traversal_id=test_run_data.test_traversal_id
        )
        if not test_traversal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test traversal with id {test_run_data.test_traversal_id} not found",
            )

        created_test_run = TestRunRepo.create(db=db_session, test_run_data=test_run_data)
        return ResponseTestRun(
            id=created_test_run.id,
            test_traversal_id=created_test_run.test_traversal_id,
            browser_config_id=created_test_run.browser_config_id,
            run_type=created_test_run.run_type,
            origin=created_test_run.origin,
            repair_was_needed=created_test_run.repair_was_needed,
            started_at=created_test_run.started_at,
            finished_at=created_test_run.finished_at,
            current_state=created_test_run.current_state,
            history=[],  # Empty history for new test runs
            run_gif=created_test_run.run_gif,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test run: {str(e)}",
        )


@test_runs_router.get(
    "/",
    response_model=PaginatedResponseExtendedTestRun,
    summary="Get All Test Runs",
    description="Retrieve all test runs with pagination, sorting, and test traversal filtering",
    responses={
        200: create_success_response(
            "Test runs retrieved successfully", PaginatedResponseExtendedTestRun
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_all_test_runs(
    page: int = 1,
    page_size: int = 10,
    sort_order: str = "desc",
    test_traversal_id: Optional[str] = None,
    db_session: Session = Depends(get_db),
) -> PaginatedResponseExtendedTestRun:
    """
    Retrieve all test runs with pagination, sorting, and test traversal filtering.

    This endpoint returns a paginated list of extended test runs in the system,
    sorted by start date (started_at). The most recent test runs are returned first by default.
    Each test run includes associated browser configurations and execution history.
    Optionally filter by test traversal ID to get only test runs for a specific test traversal.

    Args:
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        sort_order: Sort order - "asc" for oldest first, "desc" for newest first (default: "desc")
        test_traversal_id: Optional test traversal ID to filter by (default: None - returns all test runs)
        db_session: Database session

    Returns:
        PaginatedResponseExtendedTestRun: Paginated list of extended test runs with metadata
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

        # Handle test_traversal_id filtering
        if test_traversal_id:
            test_traversal = TestTraversalRepo.get_by_id(
                db=db_session, test_traversal_id=test_traversal_id
            )
            if not test_traversal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Test traversal with id {test_traversal_id} not found",
                )

        # Get extended test runs with sorting, pagination, and filtering
        extended_test_runs = TestRunRepo.get_all_extended_with_sorting_and_filter(
            db=db_session,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            test_traversal_id=test_traversal_id,
        )

        # Get total count for pagination metadata
        total_count = TestRunRepo.count_with_filter(
            db=db_session, test_traversal_id=test_traversal_id
        )

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedResponseExtendedTestRun(
            items=extended_test_runs,
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
            detail=f"Failed to retrieve test runs: {str(e)}",
        )


@test_runs_router.get(
    "/{test_run_id:str}",
    response_model=ExtendedResponseTestRun,
    summary="Get Test Run by ID (Extended)",
    description="Retrieve a specific test run by its ID with extended details including browser config and history",
    responses={
        200: create_success_response("Test run retrieved successfully", ExtendedResponseTestRun),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_test_run_by_id(
    test_run_id: str,
    db_session: Session = Depends(get_db),
) -> ExtendedResponseTestRun:
    """
    Retrieve a specific test run by its unique identifier with extended details.

    This endpoint returns comprehensive test run information including:
    - Basic test run details
    - Associated browser configuration
    - Complete execution history
    - All test execution tracking information
    """
    try:
        extended_test_run = TestRunRepo.get_extended_by_id(db=db_session, test_run_id=test_run_id)

        if not extended_test_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test run with id {test_run_id} not found",
            )

        return extended_test_run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test run: {str(e)}",
        )


@test_runs_router.put(
    "/{test_run_id:str}",
    response_model=ResponseTestRun,
    summary="Update Test Run",
    description="Update an existing test run",
    responses={
        200: create_success_response("Test run updated successfully", ResponseTestRun),
        **COMMON_ERROR_RESPONSES,
    },
)
async def update_test_run(
    test_run_id: str,
    test_run_data: UpdateTestRun,
    db_session: Session = Depends(get_db),
) -> ResponseTestRun:
    """
    Update an existing test run with new data.

    This endpoint allows updating test run state, timing, and execution details.
    The relationships to test traversal and browser config remain unchanged.
    """
    try:
        updated_test_run = TestRunRepo.update(
            db=db_session, test_run_id=test_run_id, test_run_data=test_run_data
        )

        if not updated_test_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test run with id {test_run_id} not found",
            )

        return ResponseTestRun(
            id=updated_test_run.id,
            test_traversal_id=updated_test_run.test_traversal_id,
            browser_config_id=updated_test_run.browser_config_id,
            run_type=updated_test_run.run_type,
            origin=updated_test_run.origin,
            repair_was_needed=updated_test_run.repair_was_needed,
            started_at=updated_test_run.started_at,
            finished_at=updated_test_run.finished_at,
            current_state=updated_test_run.current_state,
            history=[],  # Simplified - could be enhanced to include actual history
            run_gif=updated_test_run.run_gif,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test run: {str(e)}",
        )


@test_runs_router.delete(
    "/{test_run_id:str}",
    response_model=ResponseTestRun,
    summary="Delete Test Run",
    description="Delete a test run by its ID",
    responses={
        200: create_success_response("Test run deleted successfully", ResponseTestRun),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_test_run(
    test_run_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseTestRun:
    """
    Delete a test run from the system.

    This endpoint permanently removes a test run and returns the deleted test run information.
    """
    try:
        # First get the test run to return it after deletion
        test_run = TestRunRepo.get_by_id(db=db_session, test_run_id=test_run_id)

        if not test_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test run with id {test_run_id} not found",
            )

        # Delete the test run
        success = TestRunRepo.delete(db=db_session, test_run_id=test_run_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete test run with id {test_run_id}",
            )

        return ResponseTestRun(
            id=test_run.id,
            test_traversal_id=test_run.test_traversal_id,
            browser_config_id=test_run.browser_config_id,
            run_type=test_run.run_type,
            origin=test_run.origin,
            repair_was_needed=test_run.repair_was_needed,
            started_at=test_run.started_at,
            finished_at=test_run.finished_at,
            current_state=test_run.current_state,
            history=[],  # Simplified - could be enhanced to include actual history
            run_gif=test_run.run_gif,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete test run: {str(e)}",
        )


@test_runs_router.get(
    "/project/{project_id:str}",
    response_model=PaginatedResponseExtendedTestRun,
    summary="Get Test Runs by Project",
    description="Retrieve all test runs for a specific project with pagination and sorting",
    responses={
        200: create_success_response(
            "Test runs retrieved successfully", PaginatedResponseExtendedTestRun
        ),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_test_runs_by_project(
    project_id: str,
    page: int = 1,
    page_size: int = 10,
    sort_order: str = "desc",
    db_session: Session = Depends(get_db),
) -> PaginatedResponseExtendedTestRun:
    """
    Retrieve all test runs for a specific project with pagination and sorting.

    This endpoint returns a paginated list of extended test runs for the specified project,
    sorted by start date (started_at). The most recent test runs are returned first by default.
    Each test run includes associated browser configurations and execution history.

    Args:
        project_id: Project identifier
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        sort_order: Sort order - "asc" for oldest first, "desc" for newest first (default: "desc")
        db_session: Database session

    Returns:
        PaginatedResponseExtendedTestRun: Paginated list of extended test runs with metadata
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

        # Validate that the project exists
        from app.repo.project_repo import ProjectRepo

        project = ProjectRepo.get_by_id(db=db_session, project_id=project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found",
            )

        # Get extended test runs with sorting, pagination, and filtering by project
        extended_test_runs = TestRunRepo.get_all_extended_by_project_id_with_sorting_and_filter(
            db=db_session,
            project_id=project_id,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
        )

        # Get total count for pagination metadata
        total_count = TestRunRepo.count_by_project_id(db=db_session, project_id=project_id)

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        return PaginatedResponseExtendedTestRun(
            items=extended_test_runs,
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
            detail=f"Failed to retrieve test runs: {str(e)}",
        )
