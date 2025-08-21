"""
Test Run Repository

This module provides static methods for CRUD operations on TestRun entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, delete, select

from app.db.browser_config import BrowserConfig
from app.db.history_element import HistoryElement
from app.db.test_case import TestCase
from app.db.test_run import RunOrigin, RunState, RunType, TestRun
from app.db.test_traversal import TestTraversal
from app.schemas.communication.test_run import (
    ExtendedResponseBrainState,
    ExtendedResponseHistoryElement,
    ExtendedResponseTestRun,
    PaginatedResponseExtendedTestRun,
)
from app.schemas.crud.browser_config import ResponseBrowserConfig
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
    def delete_all(db: Session) -> bool:
        db.exec(delete(TestRun))  # type: ignore
        db.commit()
        return True

    @staticmethod
    def get_all_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        project_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs with pagination, sorting, and filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            project_id: Optional project ID to filter by (default: None - returns all test runs)
            test_case_id: Optional test case ID to filter by (default: None - returns all test runs)
            search: Optional search term to filter by test case name or description (default: None)
            status: Optional status to filter by - "pending", "passed", "failed" (default: None)

        Returns:
            Sequence[TestRun]: List of test runs sorted by start date (started_at)
        """
        # Calculate skip based on page and page_size
        skip = (page - 1) * page_size

        # Build the base query with joins for search, test_case_id, and project_id filtering
        if search or test_case_id or project_id:
            # Join with TestTraversal and TestCase for search, test case, and project filtering
            base_statement = select(TestRun).join(TestTraversal).join(TestCase)
        else:
            base_statement = select(TestRun)

        # Apply filters
        filters = []

        if project_id:
            filters.append(TestCase.project_id == project_id)

        if test_case_id:
            filters.append(TestCase.id == test_case_id)

        if search:
            # Search in test case name and description
            search_term = f"%{search}%"
            search_filter = col(TestCase.test_name).ilike(search_term) | col(
                TestCase.test_description
            ).ilike(search_term)
            filters.append(search_filter)  # type: ignore

        if status:
            # Frontend now sends exact backend values (PENDING, FINISHED, FAILED)
            if status in [RunState.PENDING, RunState.FINISHED, RunState.FAILED]:
                filters.append(TestRun.current_state == status)

        # Apply all filters
        if filters:
            base_statement = base_statement.where(*filters)

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
    def count_with_filter(
        db: Session,
        project_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Get the total number of test runs with filtering.

        Args:
            db: Database session
            project_id: Optional project ID to filter by (default: None - counts all test runs)
            test_case_id: Optional test case ID to filter by (default: None - counts all test runs)
            search: Optional search term to filter by test case name or description (default: None)
            status: Optional status to filter by - "pending", "passed", "failed" (default: None)

        Returns:
            int: Total number of test runs matching the filters
        """
        # Build the base query with joins for search, test_case_id, and project_id filtering
        if search or test_case_id or project_id:
            # Join with TestTraversal and TestCase for search, test case, and project filtering
            base_statement = select(TestRun.id).join(TestTraversal).join(TestCase)
        else:
            base_statement = select(TestRun.id)

        # Apply filters
        filters = []

        if project_id:
            filters.append(TestCase.project_id == project_id)

        if test_case_id:
            filters.append(TestCase.id == test_case_id)

        if search:
            # Search in test case name and description
            search_term = f"%{search}%"
            search_filter = col(TestCase.test_name).ilike(search_term) | col(
                TestCase.test_description
            ).ilike(search_term)
            filters.append(search_filter)  # type: ignore

        if status:
            # Frontend now sends exact backend values (PENDING, FINISHED, FAILED)
            if status in [RunState.PENDING, RunState.FINISHED, RunState.FAILED]:
                filters.append(TestRun.current_state == status)

        # Apply all filters
        if filters:
            base_statement = base_statement.where(*filters)

        return len(db.exec(base_statement).all())

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
        Retrieve an extended test run response with nested browser config, test case, and history data.

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

        # Get test case information through test traversal
        test_case_statement = (
            select(TestCase)
            .join(TestTraversal)
            .where(TestTraversal.id == test_run.test_traversal_id)
        )
        test_case = db.exec(test_case_statement).first()

        # Convert test case to dict to avoid circular import
        response_test_case = None
        if test_case:
            response_test_case = {
                "id": test_case.id,
                "project_id": test_case.project_id,
                "document_id": test_case.document_id,
                "created_at": test_case.created_at.isoformat() if test_case.created_at else None,
                "updated_at": test_case.updated_at.isoformat() if test_case.updated_at else None,
                "test_name": test_case.test_name,
                "test_description": test_case.test_description,
                "test_goal": test_case.test_goal,
                "extra_rules": test_case.extra_rules or [],
                "url_route": test_case.url_route,
                "allowed_domains": test_case.allowed_domains or [],
                "priority": test_case.priority.value if test_case.priority else None,
                "category": test_case.category,
            }

        # Get extended brain states for this test run
        repo_instance = TestRunRepo()
        extended_brain_states = repo_instance.get_extended_brain_states_by_test_traversal_id(
            db, test_run.test_traversal_id
        )

        return ExtendedResponseTestRun(
            id=test_run.id,
            test_traversal_id=test_run.test_traversal_id,
            browser_config_id=test_run.browser_config_id,
            run_type=test_run.run_type.value,
            origin=test_run.origin.value,
            repair_was_needed=test_run.repair_was_needed,
            current_state=test_run.current_state.value,
            started_at=test_run.started_at,
            finished_at=test_run.finished_at,
            run_gif=test_run.run_gif,
            browser_config=response_browser_config,
            test_case=response_test_case,
            brain_states=extended_brain_states,
            failed_at_launch=None,  # Default value for existing runs
        )

    @staticmethod
    def get_all_extended_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        project_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ExtendedResponseTestRun]:
        """
        Retrieve all test runs with extended responses, pagination, sorting, and filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            project_id: Optional project ID to filter by (default: None - returns all test runs)
            test_case_id: Optional test case ID to filter by (default: None - returns all test runs)
            search: Optional search term to filter by test case name or description (default: None)
            status: Optional status to filter by - "pending", "passed", "failed" (default: None)

        Returns:
            List[ExtendedResponseTestRun]: List of extended test runs sorted by creation date
        """
        # Get basic test runs with pagination and filtering
        test_runs = TestRunRepo.get_all_with_sorting_and_filter(
            db=db,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            project_id=project_id,
            test_case_id=test_case_id,
            search=search,
            status=status,
        )

        # Convert to extended responses
        extended_test_runs = []
        for test_run in test_runs:
            extended_test_run = TestRunRepo.get_extended_by_id(db, test_run.id)
            if extended_test_run:
                extended_test_runs.append(extended_test_run)

        return extended_test_runs

    @staticmethod
    def get_all_by_test_case_id_with_sorting_and_filter(
        db: Session,
        test_case_id: str,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
    ) -> Sequence[TestRun]:
        """
        Retrieve all test runs for a specific test case with pagination and sorting.

        This method gets all test traversals for the given test case, then retrieves
        all test runs for those traversals with pagination and sorting.

        Args:
            db: Database session
            test_case_id: Test case identifier
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")

        Returns:
            Sequence[TestRun]: List of test runs sorted by started_at date
        """
        # Get all test traversal IDs for the test case
        from app.repo.test_traversal_repo import TestTraversalRepo

        test_traversals = TestTraversalRepo.get_by_test_case_id(db, test_case_id)
        if not test_traversals:
            return []

        traversal_ids = [tt.id for tt in test_traversals]

        # Build the query with pagination and sorting
        statement = select(TestRun).where(col(TestRun.test_traversal_id).in_(traversal_ids))

        # Apply sorting
        if sort_order.lower() == "desc":
            statement = statement.order_by(col(TestRun.started_at).desc())
        else:
            statement = statement.order_by(col(TestRun.started_at).asc())

        # Apply pagination
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        return db.exec(statement).all()

    @staticmethod
    def get_all_extended_by_test_case_id_with_sorting_and_filter(
        db: Session,
        test_case_id: str,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
    ) -> List[ExtendedResponseTestRun]:
        """
        Retrieve all extended test runs for a specific test case with pagination and sorting.

        This method gets all test traversals for the given test case, then retrieves
        all extended test runs for those traversals with pagination and sorting.

        Args:
            db: Database session
            test_case_id: Test case identifier
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")

        Returns:
            List[ExtendedResponseTestRun]: List of extended test runs sorted by started_at date
        """
        # Get basic test runs with pagination and filtering
        test_runs = TestRunRepo.get_all_by_test_case_id_with_sorting_and_filter(
            db=db,
            test_case_id=test_case_id,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
        )

        # Convert to extended responses
        extended_test_runs = []
        for test_run in test_runs:
            extended_test_run = TestRunRepo.get_extended_by_id(db, test_run.id)
            if extended_test_run:
                extended_test_runs.append(extended_test_run)

        return extended_test_runs

    @staticmethod
    def count_by_test_case_id(db: Session, test_case_id: str) -> int:
        """
        Get the total number of test runs for a specific test case.

        This method counts all test runs across all test traversals for the given test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            int: Total number of test runs for the test case
        """
        # Get all test traversal IDs for the test case
        from app.repo.test_traversal_repo import TestTraversalRepo

        test_traversals = TestTraversalRepo.get_by_test_case_id(db, test_case_id)
        if not test_traversals:
            return 0

        traversal_ids = [tt.id for tt in test_traversals]

        # Count test runs for those traversals
        statement = select(TestRun).where(col(TestRun.test_traversal_id).in_(traversal_ids))
        test_runs = db.exec(statement).all()
        return len(test_runs)

    def get_extended_brain_states_by_test_traversal_id(
        self, db: Session, test_traversal_id: str
    ) -> List[ExtendedResponseBrainState]:
        """
        Get extended brain states for a test traversal with history elements.

        Args:
            db: Database session
            test_traversal_id: Test traversal ID

        Returns:
            List of extended brain states with history elements
        """
        from sqlmodel import col, select

        from app.db.action import Action
        from app.db.brain_state import BrainState
        from app.db.history_element import HistoryElement
        from app.schemas.communication.test_run import (
            ExtendedResponseBrainState,
            ExtendedResponseHistoryElement,
        )

        # Get brain states with their history elements and action data
        statement = (
            select(BrainState, HistoryElement, Action)
            .join(Action, col(BrainState.id) == col(Action.brain_state_id))
            .join(HistoryElement, col(Action.id) == col(HistoryElement.action_id))
            .where(BrainState.test_traversal_id == test_traversal_id)
            .order_by(col(BrainState.idx_in_run).asc(), col(HistoryElement.action_started_at).asc())
        )

        results = db.exec(statement).all()

        # Group history elements by brain state
        brain_state_history_map = {}
        brain_state: BrainState

        for brain_state, history_element, action in results:
            if brain_state.id not in brain_state_history_map:
                brain_state_history_map[brain_state.id] = {
                    "brain_state": brain_state,
                    "history_elements": [],
                }

            # Create extended history element with both history and action data
            extended_history_element = ExtendedResponseHistoryElement(
                # History element fields
                id=history_element.id,
                test_run_id=history_element.test_run_id,
                action_id=history_element.action_id,
                action_started_at=history_element.action_started_at,
                action_finished_at=history_element.action_finished_at,
                history_element_state=history_element.history_element_state.value,
                screenshot=history_element.screenshot,
                # Action fields
                action=action.action,
                dom_element_data=action.dom_element_data,
                valid=action.valid,
                idx_in_brain_state=action.idx_in_brain_state,
            )
            brain_state_history_map[brain_state.id]["history_elements"].append(
                extended_history_element
            )

        # Convert to response schemas
        extended_brain_states = []
        for brain_state_data in brain_state_history_map.values():
            brain_state = brain_state_data["brain_state"]  # type: ignore
            history_elements: List[ExtendedResponseHistoryElement] = brain_state_data["history_elements"]  # type: ignore

            extended_brain_state = ExtendedResponseBrainState(
                id=brain_state.id,
                test_traversal_id=brain_state.test_traversal_id,
                idx_in_run=brain_state.idx_in_run,
                valid=brain_state.valid,
                evaluation_previous_goal=brain_state.evaluation_previous_goal,
                memory=brain_state.memory,
                next_goal=brain_state.next_goal,
                history_elements=history_elements,
            )
            extended_brain_states.append(extended_brain_state)

        return extended_brain_states

    @staticmethod
    def get_extended_brain_states_by_traversal_ids(
        db: Session, traversal_ids: List[str]
    ) -> Dict[str, List[ExtendedResponseBrainState]]:
        """
        Get extended brain states for multiple traversals in a single optimized query.

        Args:
            db: Database session
            traversal_ids: List of test traversal IDs

        Returns:
            Dict[str, List[ExtendedResponseBrainState]]: Dictionary mapping traversal_id to brain states
        """
        if not traversal_ids:
            return {}

        from sqlmodel import col, select

        from app.db.action import Action
        from app.db.brain_state import BrainState
        from app.db.history_element import HistoryElement
        from app.schemas.communication.test_run import (
            ExtendedResponseBrainState,
            ExtendedResponseHistoryElement,
        )

        # Get brain states with their history elements and action data for all traversals
        statement = (
            select(BrainState, HistoryElement, Action)
            .join(Action, col(BrainState.id) == col(Action.brain_state_id))
            .join(HistoryElement, col(Action.id) == col(HistoryElement.action_id))
            .where(col(BrainState.test_traversal_id).in_(traversal_ids))
            .order_by(
                col(BrainState.test_traversal_id).asc(),
                col(BrainState.idx_in_run).asc(),
                col(HistoryElement.action_started_at).asc(),
            )
        )

        results = db.exec(statement).all()

        # Group history elements by brain state, then by traversal
        brain_state_history_map: Dict[str, Dict[str, Any]] = {}
        brain_state: BrainState

        for brain_state, history_element, action in results:
            brain_state_id = brain_state.id
            traversal_id = brain_state.test_traversal_id

            if brain_state_id not in brain_state_history_map:
                brain_state_history_map[brain_state_id] = {
                    "brain_state": brain_state,
                    "traversal_id": traversal_id,
                    "history_elements": [],
                }

            # Create extended history element with both history and action data
            extended_history_element = ExtendedResponseHistoryElement(
                # History element fields
                id=history_element.id,
                test_run_id=history_element.test_run_id,
                action_id=history_element.action_id,
                action_started_at=history_element.action_started_at,
                action_finished_at=history_element.action_finished_at,
                history_element_state=history_element.history_element_state.value,
                screenshot=history_element.screenshot,
                # Action fields
                action=action.action,
                dom_element_data=action.dom_element_data,
                valid=action.valid,
                idx_in_brain_state=action.idx_in_brain_state,
            )
            brain_state_history_map[brain_state_id]["history_elements"].append(
                extended_history_element
            )

        # Convert to response schemas grouped by traversal
        brain_states_by_traversal: Dict[str, List[ExtendedResponseBrainState]] = {}

        for brain_state_data in brain_state_history_map.values():
            brain_state = brain_state_data["brain_state"]  # type: ignore
            traversal_id = brain_state_data["traversal_id"]  # type: ignore
            history_elements: List[ExtendedResponseHistoryElement] = brain_state_data["history_elements"]  # type: ignore

            extended_brain_state = ExtendedResponseBrainState(
                id=brain_state.id,
                test_traversal_id=brain_state.test_traversal_id,
                idx_in_run=brain_state.idx_in_run,
                valid=brain_state.valid,
                evaluation_previous_goal=brain_state.evaluation_previous_goal,
                memory=brain_state.memory,
                next_goal=brain_state.next_goal,
                history_elements=history_elements,
            )

            if traversal_id not in brain_states_by_traversal:
                brain_states_by_traversal[traversal_id] = []
            brain_states_by_traversal[traversal_id].append(extended_brain_state)

        return brain_states_by_traversal

    @staticmethod
    def get_test_traversal_ids_from_test_runs(db: Session, test_run_ids: List[str]) -> List[str]:
        """
        Get test traversal IDs from a list of test run IDs.

        Args:
            db: Database session
            test_run_ids: List of test run IDs

        Returns:
            List[str]: List of unique test traversal IDs
        """
        if not test_run_ids:
            return []

        statement = select(TestRun.test_traversal_id).where(col(TestRun.id).in_(test_run_ids))
        traversal_ids = db.exec(statement).all()
        return list(set(traversal_ids))  # Remove duplicates

    @staticmethod
    def get_ongoing_test_run_ids_by_traversal_ids(
        db: Session, traversal_ids: List[str]
    ) -> Sequence[str]:
        """
        Get ongoing test runs as extended responses for the specified traversal IDs.

        Args:
            db: Database session
            traversal_ids: List of test traversal IDs to check

        Returns:
            Sequence[str]: List of ongoing test run ids
        """
        if not traversal_ids:
            return []

        statement = select(TestRun.id).where(
            col(TestRun.test_traversal_id).in_(traversal_ids),
            TestRun.current_state == RunState.PENDING,
        )
        ongoing_test_runs = db.exec(statement).all()

        return ongoing_test_runs

    @staticmethod
    def get_traversal_ids_with_completed_runs(db: Session, traversal_ids: List[str]) -> List[str]:
        """
        Get traversal IDs that have at least one completed test run.

        Args:
            db: Database session
            traversal_ids: List of test traversal IDs to check

        Returns:
            List[str]: List of traversal IDs that have completed test runs
        """
        if not traversal_ids:
            return []

        statement = (
            select(TestRun.test_traversal_id)
            .where(
                col(TestRun.test_traversal_id).in_(traversal_ids),
                TestRun.current_state == RunState.FINISHED,
            )
            .distinct()
        )
        completed_traversal_ids = db.exec(statement).all()
        return list(completed_traversal_ids)

    @staticmethod
    def create_test_runs_for_traversals(
        db: Session,
        traversal_ids: List[str],
        run_type: RunType = RunType.AGENTIC,
        origin: RunOrigin = RunOrigin.USER,
    ) -> List[TestRun]:
        """
        Create new test runs for the specified test traversals.

        Args:
            db: Database session
            traversal_ids: List of test traversal IDs to create test runs for
            run_type: Type of test run to create (default: AGENTIC)
            origin: Origin of the test run (default: USER)

        Returns:
            List[TestRun]: List of created test runs
        """
        if not traversal_ids:
            return []

        created_test_runs = []

        for traversal_id in traversal_ids:
            # Get the test traversal to get browser config ID
            from app.repo.test_traversal_repo import TestTraversalRepo

            test_traversal = TestTraversalRepo.get_by_id(db, traversal_id)
            if not test_traversal:
                continue

            # Create new test run
            test_run_data = CreateTestRun(
                test_traversal_id=traversal_id,
                browser_config_id=test_traversal.browser_config_id,
                run_type=run_type,
                origin=origin,
                repair_was_needed=False,
                current_state=RunState.PENDING,
                run_gif="",  # Will be populated during execution
            )

            test_run = TestRunRepo.create(db, test_run_data)
            created_test_runs.append(test_run)

        return created_test_runs

    @staticmethod
    def get_brain_states_for_replay(
        db: Session, test_traversal_id: str
    ) -> List[ExtendedResponseBrainState]:
        """
        Get brain states from the most recent successful test run for replay purposes.
        Returns brain states with empty history elements.

        Args:
            db: Database session
            test_traversal_id: Test traversal ID to get brain states for

        Returns:
            List[ExtendedResponseBrainState]: Brain states with empty history elements
        """
        # Get the most recent successful test run for this traversal
        statement = (
            select(TestRun)
            .where(
                TestRun.test_traversal_id == test_traversal_id,
                TestRun.current_state == RunState.FINISHED,
            )
            .order_by(col(TestRun.started_at).desc())
        )
        latest_successful_run = db.exec(statement).first()

        if not latest_successful_run:
            return []  # No previous successful run, return empty brain states

        # Get brain states from the latest successful run
        repo_instance = TestRunRepo()
        original_brain_states = repo_instance.get_extended_brain_states_by_test_traversal_id(
            db, test_traversal_id
        )

        # Copy brain states but clear history elements
        replay_brain_states = []
        for brain_state in original_brain_states:
            replay_brain_state = ExtendedResponseBrainState(
                id=brain_state.id,
                test_traversal_id=brain_state.test_traversal_id,
                idx_in_run=brain_state.idx_in_run,
                valid=brain_state.valid,
                evaluation_previous_goal=brain_state.evaluation_previous_goal,
                memory=brain_state.memory,
                next_goal=brain_state.next_goal,
                history_elements=[],  # Empty history elements for replay
            )
            replay_brain_states.append(replay_brain_state)

        return replay_brain_states
