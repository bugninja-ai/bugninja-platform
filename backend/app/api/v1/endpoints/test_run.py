import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import List, Optional, Tuple

from bugninja import (  # type: ignore
    BugninjaClient,
    BugninjaConfig,
    BugninjaTask,
    Traversal,
)
from bugninja.events.manager import EventPublisherManager  # type: ignore
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from rich import print as rich_print
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.db.test_case import TestCase
from app.db.test_run import RunOrigin, RunType
from app.interface.bugninja_db_write_publisher import DBWriteEventPublisher
from app.interface.bugninja_interface import BugninjaInterface
from app.repo.test_case_repo import TestCaseRepo
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
pp_executor = ProcessPoolExecutor()


# Helper functions for execution endpoints
def _validate_test_case_exists(test_case_id: str, db_session: Session) -> TestCase:
    """Validate that a test case exists and return it."""
    test_case = TestCaseRepo.get_by_id(db=db_session, test_case_id=test_case_id)
    if not test_case:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found",
        )
    return test_case


def _categorize_traversals(
    traversal_ids: List[str], db_session: Session
) -> Tuple[List[str], List[str]]:
    """Categorize traversals into initial and replay based on completion status."""
    if not traversal_ids:
        return [], []

    categories = TestTraversalRepo.categorize_traversals_by_completion_status(
        db_session, traversal_ids
    )

    return categories["initial"], categories["replay"]


def _run_specific_task(run_id: str, traversal_to_do: Traversal) -> None:
    # TODO! important  distinction: here we are only using the viewport sizes from the browserconfig
    #! there has to be a way in the future to map each and every single browserconfig aspect to the client
    #! but for testing purposes we will stick to this solution for now

    rich_print(traversal_to_do)

    client = BugninjaClient(
        config=BugninjaConfig(
            headless=True,
            viewport_height=traversal_to_do.browser_config.viewport.get("height", 1920),
            viewport_width=traversal_to_do.browser_config.viewport.get("width", 768),
        ),
        event_manager=EventPublisherManager([DBWriteEventPublisher()]),
    )

    task = BugninjaTask(
        run_id=run_id,
        description=traversal_to_do.test_case,
        max_steps=150,
        allowed_domains=traversal_to_do.browser_config.allowed_domains,
        secrets=traversal_to_do.secrets,
    )

    asyncio.run(client.run_task(task))


@test_runs_router.post(
    "/",
    response_model=ResponseTestRun,
    summary="Create Test Run",
    description="Create a new test run with the provided data",
    status_code=http_status.HTTP_201_CREATED,
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
                status_code=http_status.HTTP_404_NOT_FOUND,
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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    project_id: Optional[str] = None,
    test_case_id: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db_session: Session = Depends(get_db),
) -> PaginatedResponseExtendedTestRun:
    """
    Retrieve all test runs with pagination, sorting, and filtering.

    This endpoint returns a paginated list of extended test runs in the system,
    sorted by start date (started_at). The most recent test runs are returned first by default.
    Each test run includes associated browser configurations and execution history.
    Supports filtering by project ID, test case ID, search terms, and status.

    Args:
        page: Page number (1-based, default: 1)
        page_size: Number of records per page (default: 10, max: 100)
        sort_order: Sort order - "asc" for oldest first, "desc" for newest first (default: "desc")
        project_id: Optional project ID to filter by (default: None - returns all test runs)
        test_case_id: Optional test case ID to filter by (default: None - returns all test runs)
        search: Optional search term to filter test runs by test case name or description (default: None)
        status: Optional status to filter by - "pending", "passed", "failed" (default: None - returns all statuses)
        db_session: Database session

    Returns:
        PaginatedResponseExtendedTestRun: Paginated list of extended test runs with metadata
    """
    try:
        # Rename status parameter to avoid conflict with FastAPI status module
        status_filter = status

        # Validate sort order
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="sort_order must be either 'asc' or 'desc'",
            )

        # Validate page_size
        if page_size <= 0 or page_size > 100:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="page_size must be between 1 and 100",
            )

        # Validate page
        if page <= 0:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="page must be 1 or greater",
            )

        # test_case_id filtering is handled in the repository layer

        # Get extended test runs with sorting, pagination, and filtering
        extended_test_runs = TestRunRepo.get_all_extended_with_sorting_and_filter(
            db=db_session,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            project_id=project_id,
            test_case_id=test_case_id,
            search=search,
            status=status_filter,
        )

        # Get total count for pagination metadata
        total_count = TestRunRepo.count_with_filter(
            db=db_session,
            project_id=project_id,
            test_case_id=test_case_id,
            search=search,
            status=status_filter,
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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Test run with id {test_run_id} not found",
            )

        return extended_test_run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    updated_test_run = TestRunRepo.update(
        db=db_session, test_run_id=test_run_id, test_run_data=test_run_data
    )

    if not updated_test_run:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
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
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Test run with id {test_run_id} not found",
            )

        # Delete the test run
        success = TestRunRepo.delete(db=db_session, test_run_id=test_run_id)

        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete test run: {str(e)}",
        )


@test_runs_router.post(
    "/execute-configuration/{test_case_id:str}/{browser_config_id:str}",
    response_model=ExtendedResponseTestRun,
    summary="Execute Test Run for Specific Configuration",
    description="Create new test run for a specific test case and browser configuration combination",
    responses={
        200: create_success_response("Test run queued for execution", ExtendedResponseTestRun),
        **COMMON_ERROR_RESPONSES,
    },
)
async def execute_configuration(
    test_case_id: str,
    browser_config_id: str,
    db_session: Session = Depends(get_db),
) -> ExtendedResponseTestRun:
    """
    Execute test run for a specific test case and browser configuration combination.

    This endpoint finds the test traversal for the given test case and browser config,
    then creates a new test run for that traversal (if it doesn't have ongoing runs).
    """
    # Validate that the test case exists
    _validate_test_case_exists(test_case_id, db_session)

    # Get the specific test traversal
    test_traversal = TestTraversalRepo.get_by_test_case_and_browser_config(
        db=db_session, test_case_id=test_case_id, browser_config_id=browser_config_id
    )

    if not test_traversal:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"No test traversal found for test case with id '{test_case_id}' and browser config  with id '{browser_config_id}'",
        )

    initial_traversal_ids, _ = _categorize_traversals([test_traversal.id], db_session)

    if not initial_traversal_ids:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"The test traversal id '{test_traversal.id}' that you have provided is not an initial run!",
        )

    traversal_id_to_use: str = initial_traversal_ids[0]

    ongoing_test_runs_ids = TestRunRepo.get_ongoing_test_run_ids_by_traversal_ids(
        db=db_session, traversal_ids=[traversal_id_to_use]
    )

    if traversal_id_to_use in ongoing_test_runs_ids:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=f"Test traversal (not run) with id '{traversal_id_to_use}' already has an ongoing test run, therefore a new cannot be started!",
        )

    traversal_to_do: Optional[Traversal] = BugninjaInterface.get_traversal_data(
        db=db_session, traversal_id=traversal_id_to_use
    )

    if not traversal_to_do:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"There has been an error while fetching the traversal data for id '{traversal_id_to_use}'",
        )

    # ? here we should create the test run with the specified traversal and browser config
    created_test_runs = TestRunRepo.create_test_runs_for_traversals(
        db=db_session,
        traversal_ids=[traversal_id_to_use],
    )

    if not created_test_runs:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test run for traversal id '{traversal_id_to_use}'",
        )

    created_test_run_id: str = created_test_runs[0].id

    loop = asyncio.get_running_loop()
    loop.run_in_executor(
        pp_executor,
        _run_specific_task,
        created_test_run_id,
        traversal_to_do,
    )

    return_val: Optional[ExtendedResponseTestRun] = TestRunRepo.get_extended_by_id(
        db=db_session, test_run_id=created_test_run_id
    )

    if not return_val:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Test run with id '{created_test_runs[0].id}' not found after creation",
        )

    return_val.failed_at_launch = False

    # Return single test run (should be only one for configuration execution)
    return return_val


# TODO! needs further testing and validation
# @test_runs_router.post(
#     "/rerun",
#     response_model=PaginatedResponseExtendedTestRun,
#     summary="Rerun Existing Test Runs",
#     description="Create new test runs for the test traversals of existing test runs",
#     responses={
#         200: create_success_response(
#             "Test runs queued for rerun", PaginatedResponseExtendedTestRun
#         ),
#         **COMMON_ERROR_RESPONSES,
#     },
# )
# async def rerun_test_runs(
#     test_run_ids: List[str],
#     db_session: Session = Depends(get_db),
# ) -> PaginatedResponseExtendedTestRun:
#     """
#     Rerun existing test runs by creating new test runs for their test traversals.

#     This endpoint takes a list of test run IDs, extracts their test traversal IDs,
#     and creates new test runs for those traversals (if they don't have ongoing runs).
#     """
#     try:
#         # Get test traversal IDs from the provided test run IDs
#         traversal_ids = TestRunRepo.get_test_traversal_ids_from_test_runs(
#             db=db_session, test_run_ids=test_run_ids
#         )

#         if not traversal_ids:
#             raise HTTPException(
#                 status_code=http_status.HTTP_404_NOT_FOUND,
#                 detail="No valid test traversals found for the provided test run IDs",
#             )

#         extended_test_runs = _categorize_and_process_traversals(
#             traversal_ids=traversal_ids,
#             context_message="Rerun operation",
#             db_session=db_session,
#         )

#         if not extended_test_runs:
#             raise HTTPException(
#                 status_code=http_status.HTTP_404_NOT_FOUND,
#                 detail="No test runs could be created or found for the provided test run IDs",
#             )

#         # Return paginated response with all results in single page
#         total_count = len(extended_test_runs)
#         return PaginatedResponseExtendedTestRun(
#             items=extended_test_runs,
#             total_count=total_count,
#             page=1,
#             page_size=total_count,
#             total_pages=1,
#             has_next=False,
#             has_previous=False,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to rerun test runs: {str(e)}",
# )


# TODO! needs further testing and validation
# @test_runs_router.post(
#     "/execute-test-case/{test_case_id}",
#     response_model=PaginatedResponseExtendedTestRun,
#     summary="Execute All Test Runs for Test Case",
#     description="Create new test runs for all test traversals of a specific test case",
#     responses={
#         200: create_success_response("Test runs queued for execution", PaginatedResponseExtendedTestRun),
#         **COMMON_ERROR_RESPONSES,
#     },
# )
# async def execute_test_case(
#     test_case_id: str,
#     db_session: Session = Depends(get_db),
# ) -> PaginatedResponseExtendedTestRun:
#     """
#     Execute all test runs for a specific test case by creating new test runs
#     for all its test traversals.

#     This endpoint gets all test traversals for the given test case and creates
#     new test runs for those traversals (if they don't have ongoing runs).
#     """
#     try:
#         # Validate that the test case exists
#         _validate_test_case_exists(test_case_id, db_session)

#         # Get all test traversals for this test case
#         test_traversals = TestTraversalRepo.get_by_test_case_id(
#             db=db_session, test_case_id=test_case_id
#         )

#         if not test_traversals:
#             raise HTTPException(
#                 status_code=http_status.HTTP_404_NOT_FOUND,
#                 detail=f"No test traversals found for test case {test_case_id}",
#             )

#         traversal_ids = [traversal.id for traversal in test_traversals]

#         extended_test_runs = _categorize_and_process_traversals(
#             traversal_ids=traversal_ids,
#             context_message=f"Test case execution for {test_case_id}",
#             db_session=db_session,
#         )

#         if not extended_test_runs:
#             raise HTTPException(
#                 status_code=http_status.HTTP_404_NOT_FOUND,
#                 detail=f"No test runs could be created or found for test case {test_case_id}",
#             )

#         # Return paginated response with all results in single page
#         total_count = len(extended_test_runs)
#         return PaginatedResponseExtendedTestRun(
#             items=extended_test_runs,
#             total_count=total_count,
#             page=1,
#             page_size=total_count,
#             total_pages=1,
#             has_next=False,
#             has_previous=False,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to execute test case: {str(e)}",
#         )


# TODO! needs further testing and validation
# @test_runs_router.post(
#     "/execute-project/{project_id}",
#     response_model=PaginatedResponseExtendedTestRun,
#     summary="Execute All Test Runs in Project",
#     description="Create new test runs for all test traversals in a project",
#     responses={
#         200: create_success_response("Test runs queued for execution", PaginatedResponseExtendedTestRun),
#         **COMMON_ERROR_RESPONSES,
#     },
# )
# async def execute_project(
#     project_id: str,
#     db_session: Session = Depends(get_db),
# ) -> PaginatedResponseExtendedTestRun:
#     """
#     Execute all test runs in a project by creating new test runs for all test traversals.

#     This endpoint gets all test traversals for all test cases in the project and creates
#     new test runs for those traversals (if they don't have ongoing runs).
#     """
#     try:
#         # Validate that the project exists
#         _validate_project_exists(project_id, db_session)

#         # Get all test traversals for this project
#         test_traversals = TestTraversalRepo.get_all_by_project_id(
#             db=db_session, project_id=project_id
#         )

#         if not test_traversals:
#             raise HTTPException(
#                 status_code=http_status.HTTP_404_NOT_FOUND,
#                 detail=f"No test traversals found for project {project_id}",
#             )

#         traversal_ids = [traversal.id for traversal in test_traversals]

#         extended_test_runs = _categorize_and_process_traversals(
#             traversal_ids=traversal_ids,
#             context_message=f"Project execution for {project_id}",
#             db_session=db_session,
#         )

#         if not extended_test_runs:
#             raise HTTPException(
#                 status_code=http_status.HTTP_404_NOT_FOUND,
#                 detail=f"No test runs could be created or found for project {project_id}",
#             )

#         # Return paginated response with all results in single page
#         total_count = len(extended_test_runs)
#         return PaginatedResponseExtendedTestRun(
#             items=extended_test_runs,
#             total_count=total_count,
#             page=1,
#             page_size=total_count,
#             total_pages=1,
#             has_next=False,
#             has_previous=False,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to execute project: {str(e)}",
#         )
