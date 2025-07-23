"""
Test Run Repository

This module provides static methods for CRUD operations on TestRun entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import List, Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

from app.db.browser_config import BrowserConfig
from app.db.history_element import HistoryElement
from app.db.test_run import RunOrigin, RunState, RunType, TestRun
from app.schemas.communication.test_run import ExtendedResponseTestRun
from app.schemas.crud.browser_config import ResponseBrowserConfig
from app.schemas.crud.history_element import ResponseHistoryElement
from app.schemas.crud.test_run import CreateTestRun, ResponseTestRun, UpdateTestRun


class TestRunRepo:
    """
    Repository class for TestRun entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, test_run_data: CreateTestRun) -> TestRun:
        """
        Create a new test run in the database.

        Args:
            db: Database session
            test_run_data: Test run creation data

        Returns:
            TestRun: The created test run instance
        """
        test_run = TestRun(
            id=CUID().generate(),
            test_traversal_id=test_run_data.test_traversal_id,
            browser_config_id=test_run_data.browser_config_id,
            run_type=test_run_data.run_type,
            origin=test_run_data.origin,
            repair_was_needed=test_run_data.repair_was_needed,
            current_state=test_run_data.current_state,
            run_gif=test_run_data.run_gif,
        )
        db.add(test_run)
        db.commit()
        db.refresh(test_run)
        return test_run

    @staticmethod
    def get_by_id(db: Session, test_run_id: str) -> Optional[TestRun]:
        """
        Retrieve a test run by its ID.

        Args:
            db: Database session
            test_run_id: Unique test run identifier

        Returns:
            Optional[TestRun]: The test run if found, None otherwise
        """
        statement = select(TestRun).where(TestRun.id == test_run_id)
        return db.exec(statement).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[TestRun]:
        """
        Retrieve all test runs with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of test runs
        """
        statement = select(TestRun).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_all_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        test_traversal_id: Optional[str] = None,
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs with pagination, sorting, and optional test traversal filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            test_traversal_id: Optional test traversal ID to filter by (default: None - returns all test runs)

        Returns:
            Sequence[TestRun]: List of test runs sorted by start date (started_at)
        """
        # Calculate skip based on page and page_size
        skip = (page - 1) * page_size

        # Build the base query
        if test_traversal_id:
            # Filter by test traversal ID
            base_statement = select(TestRun).where(TestRun.test_traversal_id == test_traversal_id)
        else:
            # No filtering - get all test runs
            base_statement = select(TestRun)

        # Add sorting and pagination
        if sort_order.lower() == "asc":
            statement = (
                base_statement.order_by(col(TestRun.started_at).asc()).offset(skip).limit(page_size)
            )
        else:
            statement = (
                base_statement.order_by(col(TestRun.started_at).desc())
                .offset(skip)
                .limit(page_size)
            )

        return db.exec(statement).all()

    @staticmethod
    def get_by_test_traversal_id(
        db: Session, test_traversal_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of test runs for the test traversal
        """
        statement = (
            select(TestRun)
            .where(TestRun.test_traversal_id == test_traversal_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_browser_config_id(
        db: Session, browser_config_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs for a specific browser configuration.

        Args:
            db: Database session
            browser_config_id: Browser configuration identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of test runs for the browser configuration
        """
        statement = (
            select(TestRun)
            .where(TestRun.browser_config_id == browser_config_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_state(
        db: Session, state: RunState, skip: int = 0, limit: int = 100
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs with a specific state.

        Args:
            db: Database session
            state: Test run state to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of test runs with the specified state
        """
        statement = select(TestRun).where(TestRun.current_state == state).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_run_type(
        db: Session, run_type: RunType, skip: int = 0, limit: int = 100
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs with a specific run type.

        Args:
            db: Database session
            run_type: Test run type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of test runs with the specified run type
        """
        statement = select(TestRun).where(TestRun.run_type == run_type).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_origin(
        db: Session, origin: RunOrigin, skip: int = 0, limit: int = 100
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs with a specific origin.

        Args:
            db: Database session
            origin: Test run origin to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of test runs with the specified origin
        """
        statement = select(TestRun).where(TestRun.origin == origin).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_finished_runs(db: Session, skip: int = 0, limit: int = 100) -> Sequence[TestRun]:
        """
        Retrieve all finished test runs.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of finished test runs
        """
        statement = (
            select(TestRun)
            .where(TestRun.current_state == RunState.FINISHED)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_running_runs(db: Session, skip: int = 0, limit: int = 100) -> Sequence[TestRun]:
        """
        Retrieve all currently running test runs.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestRun]: List of running test runs
        """
        statement = (
            select(TestRun)
            .where(TestRun.current_state == RunState.RUNNING)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(db: Session, test_run_id: str, test_run_data: UpdateTestRun) -> Optional[TestRun]:
        """
        Update an existing test run.

        Args:
            db: Database session
            test_run_id: Unique test run identifier
            test_run_data: Test run update data

        Returns:
            Optional[TestRun]: The updated test run if found, None otherwise
        """
        test_run = TestRunRepo.get_by_id(db, test_run_id)
        if not test_run:
            return None

        for k, v in test_run_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(test_run, k, v)

        db.add(test_run)
        db.commit()
        db.refresh(test_run)
        return test_run

    @staticmethod
    def update_state(db: Session, test_run_id: str, new_state: RunState) -> Optional[TestRun]:
        """
        Update the state of a test run.

        Args:
            db: Database session
            test_run_id: Unique test run identifier
            new_state: New state for the test run

        Returns:
            Optional[TestRun]: The updated test run if found, None otherwise
        """
        test_run = TestRunRepo.get_by_id(db, test_run_id)
        if not test_run:
            return None

        test_run.current_state = new_state
        if new_state == RunState.FINISHED:
            test_run.finished_at = datetime.now(timezone.utc)

        db.add(test_run)
        db.commit()
        db.refresh(test_run)
        return test_run

    @staticmethod
    def delete(db: Session, test_run_id: str) -> bool:
        """
        Delete a test run by its ID.

        Args:
            db: Database session
            test_run_id: Unique test run identifier

        Returns:
            bool: True if test run was deleted, False if not found
        """
        test_run = TestRunRepo.get_by_id(db, test_run_id)
        if not test_run:
            return False

        db.delete(test_run)
        db.commit()
        return True

    @staticmethod
    def count_by_test_traversal(db: Session, test_traversal_id: str) -> int:
        """
        Get the total number of test runs for a test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            int: Total number of test runs for the test traversal
        """
        statement = select(TestRun).where(TestRun.test_traversal_id == test_traversal_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count_by_state(db: Session, state: RunState) -> int:
        """
        Get the total number of test runs with a specific state.

        Args:
            db: Database session
            state: Test run state to count

        Returns:
            int: Total number of test runs with the specified state
        """
        statement = select(TestRun).where(TestRun.current_state == state)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of test runs.

        Args:
            db: Database session

        Returns:
            int: Total number of test runs
        """
        statement = select(TestRun)
        return len(db.exec(statement).all())

    @staticmethod
    def count_with_filter(db: Session, test_traversal_id: Optional[str] = None) -> int:
        """
        Get the total number of test runs with optional test traversal filtering.

        Args:
            db: Database session
            test_traversal_id: Optional test traversal ID to filter by (default: None - counts all test runs)

        Returns:
            int: Total number of test runs matching the filter
        """
        if test_traversal_id:
            statement = select(TestRun.id).where(TestRun.test_traversal_id == test_traversal_id)
        else:
            statement = select(TestRun.id)

        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_test_traversal(db: Session, test_traversal_id: str) -> int:
        """
        Delete all test runs for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            int: Number of test runs deleted
        """
        statement = select(TestRun).where(TestRun.test_traversal_id == test_traversal_id)
        test_runs = db.exec(statement).all()
        count = len(test_runs)

        for test_run in test_runs:
            db.delete(test_run)

        db.commit()
        return count

    @staticmethod
    def get_latest_by_test_traversal(db: Session, test_traversal_id: str) -> Optional[TestRun]:
        """
        Get the latest test run for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            Optional[TestRun]: The latest test run if found, None otherwise
        """
        statement = (
            select(TestRun)
            .where(TestRun.test_traversal_id == test_traversal_id)
            .order_by(col(TestRun.started_at).desc())
        )
        return db.exec(statement).first()

    # Extended Response Methods

    @staticmethod
    def get_extended_by_id(db: Session, test_run_id: str) -> Optional[ExtendedResponseTestRun]:
        """
        Retrieve an extended test run response with nested browser config and history data.

        Args:
            db: Database session
            test_run_id: Unique test run identifier

        Returns:
            Optional[ExtendedResponseTestRun]: The extended test run response if found, None otherwise
        """
        # Get the test run
        test_run = TestRunRepo.get_by_id(db, test_run_id)
        if not test_run:
            return None

        # Get associated browser config
        browser_config_statement = select(BrowserConfig).where(
            BrowserConfig.id == test_run.browser_config_id
        )
        browser_config = db.exec(browser_config_statement).first()

        if not browser_config:
            return None  # Browser config is required for extended response

        # Convert browser config to ResponseBrowserConfig
        response_browser_config = ResponseBrowserConfig(
            id=browser_config.id,
            project_id=browser_config.project_id,
            browser_config=browser_config.browser_config,
            created_at=browser_config.created_at,
            updated_at=browser_config.updated_at,
        )

        # Get associated history elements
        history_statement = (
            select(HistoryElement)
            .where(HistoryElement.test_run_id == test_run_id)
            .order_by(col(HistoryElement.action_started_at).asc())
        )
        history_elements = db.exec(history_statement).all()

        # Convert history elements to ResponseHistoryElement
        response_history_elements = []
        for he in history_elements:
            response_history_element = ResponseHistoryElement(
                id=he.id,
                test_run_id=he.test_run_id,
                action_id=he.action_id,
                action_started_at=he.action_started_at,
                action_finished_at=he.action_finished_at,
                history_element_state=he.history_element_state,
                screenshot=he.screenshot,
            )
            response_history_elements.append(response_history_element)

        return ExtendedResponseTestRun(
            id=test_run.id,
            test_traversal_id=test_run.test_traversal_id,
            browser_config=response_browser_config,
            run_type=test_run.run_type,
            origin=test_run.origin,
            repair_was_needed=test_run.repair_was_needed,
            started_at=test_run.started_at,
            finished_at=test_run.finished_at,
            current_state=test_run.current_state,
            history=response_history_elements,
            run_gif=test_run.run_gif,
        )

    @staticmethod
    def get_all_extended_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        test_traversal_id: Optional[str] = None,
    ) -> List[ExtendedResponseTestRun]:
        """
        Retrieve all test runs with extended responses, pagination, sorting, and optional test traversal filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            test_traversal_id: Optional test traversal ID to filter by (default: None - returns all test runs)

        Returns:
            List[ExtendedResponseTestRun]: List of extended test runs sorted by creation date
        """
        # Get basic test runs with pagination and filtering
        test_runs = TestRunRepo.get_all_with_sorting_and_filter(
            db=db,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            test_traversal_id=test_traversal_id,
        )

        # Convert to extended responses
        extended_test_runs = []
        for test_run in test_runs:
            extended_test_run = TestRunRepo.get_extended_by_id(db, test_run.id)
            if extended_test_run:
                extended_test_runs.append(extended_test_run)

        return extended_test_runs

    @staticmethod
    def get_extended_by_test_traversal_id(
        db: Session, test_traversal_id: str, skip: int = 0, limit: int = 100
    ) -> List[ExtendedResponseTestRun]:
        """
        Retrieve all extended test runs for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ExtendedResponseTestRun]: List of extended test run responses
        """
        test_runs = TestRunRepo.get_by_test_traversal_id(db, test_traversal_id, skip, limit)
        extended_test_runs = []

        for test_run in test_runs:
            extended_test_run = TestRunRepo.get_extended_by_id(db, test_run.id)
            if extended_test_run:
                extended_test_runs.append(extended_test_run)

        return extended_test_runs
