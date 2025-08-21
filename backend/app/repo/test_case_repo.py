"""
Test Case Repository

This module provides static methods for CRUD operations on TestCase entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, delete, select

from app.db.action import Action
from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.cost import Cost
from app.db.document import Document
from app.db.history_element import HistoryElement
from app.db.secret_value import SecretValue
from app.db.secret_value_test_case import SecretValueTestCase
from app.db.test_case import TestCase
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_run import RunState, TestRun
from app.db.test_traversal import TestTraversal

# BrowserConfigRepo is imported lazily to avoid circular dependency
from app.repo.document_repo import DocumentRepo
from app.repo.project_repo import ProjectRepo
from app.repo.secret_value_repo import SecretValueRepo
from app.repo.test_traversal_repo import TestTraversalRepo
from app.schemas.communication.test_case import ExtendedResponseTestcase
from app.schemas.crud.browser_config import CreateBrowserConfig, ResponseBrowserConfig
from app.schemas.crud.document import ResponseDocument
from app.schemas.crud.secret_value import CreateSecretValue, ResponseSecretValue
from app.schemas.crud.test_case import (
    CreateTestCase,
    CreateTestCaseResponse,
    ResponseTestCase,
    UpdateTestCase,
)
from app.schemas.crud.test_traversal import CreateTestTraversal, ResponseTestTraversal


class TestCaseRepo:
    """
    Repository class for TestCase entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(
        db: Session, test_case_data: CreateTestCase, overwrite_test_case_id: Optional[str] = None
    ) -> TestCase:
        """
        Create a new test case in the database.

        Args:
            db: Database session
            test_case_data: Test case creation data

        Returns:
            TestCase: The created test case instance
        """

        # Get project name and count of existing test cases
        project = ProjectRepo.get_by_id(db, test_case_data.project_id)
        if not project:
            raise ValueError(f"Project with id {test_case_data.project_id} not found")

        # Count existing test cases for this project
        existing_test_cases_count = TestCaseRepo.count_by_project(db, test_case_data.project_id)

        # Generate ID following the template: {project_name}-TC-{number_of_Test_cases_in_project+1}-{generated_CUID}

        if not overwrite_test_case_id:
            test_case_number = existing_test_cases_count + 1
            generated_cuid = CUID().generate()
            test_case_id = f"{project.name}-TC-{test_case_number}-{generated_cuid}"
        else:
            test_case_id = overwrite_test_case_id

        test_case = TestCase(
            id=test_case_id,
            project_id=test_case_data.project_id,
            document_id=test_case_data.document_id,
            test_name=test_case_data.test_name,
            test_description=test_case_data.test_description,
            test_goal=test_case_data.test_goal,
            extra_rules=test_case_data.extra_rules,
            url_route=test_case_data.url_route,
            allowed_domains=test_case_data.allowed_domains,
            priority=test_case_data.priority,
            category=test_case_data.category,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(test_case)
        db.commit()
        db.refresh(test_case)
        return test_case

    @staticmethod
    def get_by_id(db: Session, test_case_id: str) -> Optional[TestCase]:
        """
        Retrieve a test case by its ID.

        Args:
            db: Database session
            test_case_id: Unique test case identifier

        Returns:
            Optional[TestCase]: The test case if found, None otherwise
        """
        statement = select(TestCase).where(TestCase.id == test_case_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_all(db: Session) -> bool:
        db.exec(delete(TestCase))  # type: ignore
        db.commit()
        return True

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[TestCase]:
        """
        Retrieve all test cases with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestCase]: List of test cases
        """
        statement = select(TestCase).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_all_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        project_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Sequence[TestCase]:
        """
        Retrieve all test cases with pagination, sorting, filtering, and search.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            project_id: Optional project ID to filter by (default: None - returns all test cases)
            search: Optional search term to filter by test name or description (default: None)

        Returns:
            Sequence[TestCase]: List of test cases sorted by creation date
        """
        # Calculate skip based on page and page_size
        skip = (page - 1) * page_size

        # Build the base query
        base_statement = select(TestCase)

        # Apply filters
        filters = []

        if project_id:
            filters.append(TestCase.project_id == project_id)

        if search:
            # Search in test case name and description
            search_term = f"%{search}%"
            search_filter = col(TestCase.test_name).ilike(search_term) | col(
                TestCase.test_description
            ).ilike(search_term)
            filters.append(search_filter)  # type: ignore

        # Apply all filters
        if filters:
            base_statement = base_statement.where(*filters)

        # Add sorting and pagination
        if sort_order.lower() == "asc":
            statement = (
                base_statement.order_by(col(TestCase.created_at).asc())
                .offset(skip)
                .limit(page_size)
            )
        else:
            statement = (
                base_statement.order_by(col(TestCase.created_at).desc())
                .offset(skip)
                .limit(page_size)
            )

        return db.exec(statement).all()

    @staticmethod
    def get_by_project_id(
        db: Session, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestCase]:
        """
        Retrieve all test cases for a specific project.

        Args:
            db: Database session
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestCase]: List of test cases for the project
        """
        statement = (
            select(TestCase).where(TestCase.project_id == project_id).offset(skip).limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(
        db: Session, test_case_id: str, test_case_data: UpdateTestCase
    ) -> Optional[TestCase]:
        """
        Update an existing test case.

        Args:
            db: Database session
            test_case_id: Unique test case identifier
            test_case_data: Test case update data

        Returns:
            Optional[TestCase]: The updated test case if found, None otherwise
        """
        test_case = TestCaseRepo.get_by_id(db, test_case_id)
        if not test_case:
            return None

        # Extract association fields before updating basic fields
        browser_config_ids_to_add = test_case_data.browser_config_ids_to_add
        browser_config_ids_to_remove = test_case_data.browser_config_ids_to_remove
        new_browser_configs = test_case_data.new_browser_configs
        secret_value_ids_to_add = test_case_data.secret_value_ids_to_add
        secret_value_ids_to_remove = test_case_data.secret_value_ids_to_remove
        new_secret_values = test_case_data.new_secret_values

        # Update basic test case fields (excluding association fields)
        update_data = test_case_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={
                "browser_config_ids_to_add",
                "browser_config_ids_to_remove",
                "new_browser_configs",
                "secret_value_ids_to_add",
                "secret_value_ids_to_remove",
                "new_secret_values",
            },
        )

        for k, v in update_data.items():
            setattr(test_case, k, v)

        test_case.updated_at = datetime.now(timezone.utc)

        db.add(test_case)
        db.commit()
        db.refresh(test_case)

        # Handle browser config associations
        TestCaseRepo._handle_browser_config_associations(
            db,
            test_case_id,
            browser_config_ids_to_add,
            browser_config_ids_to_remove,
            new_browser_configs,
            test_case.project_id,
        )

        # Handle secret value associations
        TestCaseRepo._handle_secret_value_associations(
            db,
            test_case_id,
            secret_value_ids_to_add,
            secret_value_ids_to_remove,
            new_secret_values,
            test_case.project_id,
        )

        return test_case

    @staticmethod
    def delete(db: Session, test_case_id: str) -> bool:
        """
        Delete a test case by its ID with comprehensive cascade deletion.

        This method performs cascade deletion in the following order to respect foreign key constraints:
        1. Delete all actions associated with brain states
        2. Delete all brain states associated with test traversals
        3. Delete all history elements and costs associated with test runs
        4. Delete all test runs associated with test traversals
        5. Delete all test traversals associated with this test case
        6. Delete all browser config associations (TestCaseBrowserConfig)
        7. Delete all secret value associations (SecretValueTestCase)
        8. Delete the test case itself

        This ensures that all related data is properly cleaned up before attempting
        to delete the test case, preventing foreign key constraint violations.

        Args:
            db: Database session
            test_case_id: Unique test case identifier

        Returns:
            bool: True if test case was deleted, False if not found

        Raises:
            Exception: If any database operation fails, transaction is rolled back
        """
        test_case = TestCaseRepo.get_by_id(db, test_case_id)
        if not test_case:
            return False

        try:
            # 1. Get all test traversals for this test case
            traversals = db.exec(
                select(TestTraversal).where(TestTraversal.test_case_id == test_case_id)
            ).all()

            # 2. Delete cascade starting from the deepest level: Actions -> BrainStates -> TestRuns -> TestTraversals
            for traversal in traversals:
                # 2a. Delete all actions through brain states
                brain_states = db.exec(
                    select(BrainState).where(BrainState.test_traversal_id == traversal.id)
                ).all()

                for brain_state in brain_states:
                    # Delete all actions for this brain state
                    actions = db.exec(
                        select(Action).where(Action.brain_state_id == brain_state.id)
                    ).all()
                    for action in actions:
                        db.delete(action)

                # 2b. Delete all brain states for this traversal
                for brain_state in brain_states:
                    db.delete(brain_state)

                # 2c. Delete all test runs for this traversal
                test_runs = db.exec(
                    select(TestRun).where(TestRun.test_traversal_id == traversal.id)
                ).all()

                for test_run in test_runs:
                    # Delete history elements for this test run
                    history_elements = db.exec(
                        select(HistoryElement).where(HistoryElement.test_run_id == test_run.id)
                    ).all()
                    for history_element in history_elements:
                        db.delete(history_element)

                    # Delete cost associated with this test run
                    costs = db.exec(select(Cost).where(Cost.test_run_id == test_run.id)).all()
                    for cost in costs:
                        db.delete(cost)

                    # Delete the test run itself
                    db.delete(test_run)

            # 3. Delete all test traversals
            for traversal in traversals:
                db.delete(traversal)

            # 4. Delete browser config associations (TestCaseBrowserConfig)
            browser_config_associations = db.exec(
                select(TestCaseBrowserConfig).where(
                    TestCaseBrowserConfig.test_case_id == test_case_id
                )
            ).all()
            for browser_association in browser_config_associations:
                db.delete(browser_association)

            # 5. Delete secret value associations (SecretValueTestCase)
            secret_associations = db.exec(
                select(SecretValueTestCase).where(SecretValueTestCase.test_case_id == test_case_id)
            ).all()
            for secret_association in secret_associations:
                db.delete(secret_association)

            # 6. Finally, delete the test case itself
            db.delete(test_case)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def count_by_project(db: Session, project_id: str) -> int:
        """
        Get the total number of test cases for a project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Total number of test cases for the project
        """
        statement = select(TestCase.id).where(TestCase.project_id == project_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of test cases.

        Args:
            db: Database session

        Returns:
            int: Total number of test cases
        """
        statement = select(TestCase)
        return len(db.exec(statement).all())

    @staticmethod
    def count_with_filter(
        db: Session, project_id: Optional[str] = None, search: Optional[str] = None
    ) -> int:
        """
        Get the total number of test cases with optional filtering and search.

        Args:
            db: Database session
            project_id: Optional project ID to filter by (default: None - counts all test cases)
            search: Optional search term to filter by test name or description (default: None)

        Returns:
            int: Total number of test cases matching the filters
        """
        # Build the base query
        base_statement = select(TestCase.id)

        # Apply filters
        filters = []

        if project_id:
            filters.append(TestCase.project_id == project_id)

        if search:
            # Search in test case name and description
            search_term = f"%{search}%"
            search_filter = col(TestCase.test_name).ilike(search_term) | col(
                TestCase.test_description
            ).ilike(search_term)
            filters.append(search_filter)  # type: ignore

        # Apply all filters
        if filters:
            base_statement = base_statement.where(*filters)

        return len(db.exec(base_statement).all())

    @staticmethod
    def get_browser_configs_by_test_case_id(
        db: Session, test_case_id: str
    ) -> List[ResponseBrowserConfig]:
        """
        Get all browser configs associated with a test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            List[ResponseBrowserConfig]: List of browser configs associated with the test case
        """
        # Get browser config IDs for test case from association table
        association_statement = select(TestCaseBrowserConfig.browser_config_id).where(
            TestCaseBrowserConfig.test_case_id == test_case_id
        )
        browser_config_ids = db.exec(association_statement).all()

        # If no browser configs found, return empty list
        if not browser_config_ids:
            return []

        # Get browser config objects
        browser_config_statement = select(BrowserConfig).where(
            col(BrowserConfig.id).in_([bc_id for bc_id in browser_config_ids])
        )
        browser_configs = db.exec(browser_config_statement).all()

        # Convert to response models
        response_browser_configs = []
        for browser_config in browser_configs:
            response_browser_config = ResponseBrowserConfig(
                id=browser_config.id,
                project_id=browser_config.project_id,
                browser_config=browser_config.browser_config,
                created_at=browser_config.created_at,
                updated_at=browser_config.updated_at,
            )
            response_browser_configs.append(response_browser_config)

        return response_browser_configs

    # Extended Response Methods

    @staticmethod
    def get_extended_by_id(db: Session, test_case_id: str) -> Optional[ExtendedResponseTestcase]:
        """
        Retrieve an extended test case response with nested document data.

        Args:
            db: Database session
            test_case_id: Unique test case identifier

        Returns:
            Optional[ExtendedResponseTestcase]: The extended test case response if found, None otherwise
        """
        # Get the test case
        test_case = TestCaseRepo.get_by_id(db, test_case_id)
        if not test_case:
            return None

        # Get associated document if it exists
        document = None
        if test_case.document_id:
            document_statement = select(Document).where(Document.id == test_case.document_id)
            document = db.exec(document_statement).first()

        # Convert document to ResponseDocument if it exists
        response_document = None
        if document:
            response_document = ResponseDocument(
                id=document.id,
                project_id=document.project_id,
                created_at=document.created_at,
                updated_at=document.updated_at,
                name=document.name,
                content=document.content,
            )

        # Get associated browser configs
        browser_configs = TestCaseRepo.get_browser_configs_by_test_case_id(db, test_case_id)

        # Get associated secrets through test case association
        secrets = TestCaseRepo._get_secrets_by_test_case_id(db, test_case_id)

        # Calculate execution statistics
        execution_stats = TestCaseRepo._calculate_execution_statistics(db, test_case_id)

        # Get latest run date
        latest_run_date = TestCaseRepo._get_latest_run_date(db, test_case_id)

        return ExtendedResponseTestcase(
            id=test_case.id,
            project_id=test_case.project_id,
            document=response_document,
            browser_configs=browser_configs,
            secrets=secrets,
            created_at=test_case.created_at,
            updated_at=test_case.updated_at,
            test_name=test_case.test_name,
            test_description=test_case.test_description,
            test_goal=test_case.test_goal,
            extra_rules=test_case.extra_rules,
            url_routes=test_case.url_route,  # Note: field name difference
            allowed_domains=test_case.allowed_domains,
            priority=test_case.priority,
            category=test_case.category,
            total_runs=execution_stats["total_runs"],
            passed_runs=execution_stats["passed_runs"],
            failed_runs=execution_stats["failed_runs"],
            success_rate=execution_stats["success_rate"],
            last_run_at=latest_run_date,
        )

    @staticmethod
    def _get_secrets_by_test_case_id(db: Session, test_case_id: str) -> List[ResponseSecretValue]:
        """
        Retrieve all secrets associated with a test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            List[ResponseSecretValue]: List of secret values associated with the test case
        """
        # Get all secret values associated with this test case
        secret_statement = (
            select(SecretValue)
            .join(SecretValueTestCase)
            .where(
                SecretValue.id == SecretValueTestCase.secret_value_id,
                SecretValueTestCase.test_case_id == test_case_id,
            )
        )
        secret_values = db.exec(secret_statement).all()

        # Convert to ResponseSecretValue objects
        response_secrets = [
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

        return response_secrets

    @staticmethod
    def _calculate_execution_statistics(db: Session, test_case_id: str) -> Dict[str, Any]:
        """
        Calculate execution statistics for a test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            dict: Dictionary containing execution statistics
        """

        # Get all test runs for this test case through test traversals
        test_runs_statement = (
            select(TestRun)
            .join(TestTraversal)
            .where(
                TestRun.test_traversal_id == TestTraversal.id,
                TestTraversal.test_case_id == test_case_id,
            )
        )
        test_runs = db.exec(test_runs_statement).all()

        total_runs = len(test_runs)
        # Count different states: FINISHED = passed, FAILED = failed, PENDING = in progress
        passed_runs = len([run for run in test_runs if run.current_state == RunState.FINISHED])
        failed_runs = len([run for run in test_runs if run.current_state == RunState.FAILED])

        # Calculate success rate
        success_rate = (passed_runs / total_runs * 100) if total_runs > 0 else 0.0

        return {
            "total_runs": total_runs,
            "passed_runs": passed_runs,
            "failed_runs": failed_runs,
            "success_rate": round(success_rate, 1),
        }

    @staticmethod
    def _get_latest_run_date(db: Session, test_case_id: str) -> Optional[datetime]:
        """
        Get the latest test run date for a test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            Optional[datetime]: The latest test run date if found, None otherwise
        """
        # Get all test runs for this test case through test traversals
        latest_run_statement = (
            select(TestRun.started_at)
            .join(TestTraversal)
            .where(
                TestRun.test_traversal_id == TestTraversal.id,
                TestTraversal.test_case_id == test_case_id,
            )
            .order_by(col(TestRun.started_at).desc())
            .limit(1)
        )

        result = db.exec(latest_run_statement).first()
        return result

    @staticmethod
    def get_extended_by_project_id(
        db: Session, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[ExtendedResponseTestcase]:
        """
        Retrieve all extended test cases for a specific project.

        Args:
            db: Database session
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[ExtendedResponseTestcase]: List of extended test case responses
        """
        test_cases = TestCaseRepo.get_by_project_id(db, project_id, skip, limit)
        extended_test_cases = []

        for test_case in test_cases:
            extended_test_case = TestCaseRepo.get_extended_by_id(db, test_case.id)
            if extended_test_case:
                extended_test_cases.append(extended_test_case)

        return extended_test_cases

    @staticmethod
    def get_all_extended(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[ExtendedResponseTestcase]:
        """
        Retrieve all test cases with extended responses including document data.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[ExtendedResponseTestcase]: List of extended test case responses
        """
        test_cases = TestCaseRepo.get_all(db, skip, limit)
        extended_test_cases = []

        for test_case in test_cases:
            extended_test_case = TestCaseRepo.get_extended_by_id(db, test_case.id)
            if extended_test_case:
                extended_test_cases.append(extended_test_case)

        return extended_test_cases

    # Enhanced Creation Methods

    @staticmethod
    def _validate_browser_configs(
        db: Session, browser_config_ids: List[str], project_id: str
    ) -> List[BrowserConfig]:
        """
        Validate that browser config IDs exist and belong to the specified project.

        Args:
            db: Database session
            browser_config_ids: List of browser config IDs to validate
            project_id: Project ID to validate ownership

        Returns:
            List[BrowserConfig]: List of validated browser configs

        Raises:
            ValueError: If any browser config doesn't exist or doesn't belong to project
        """
        if not browser_config_ids:
            return []

        # Lazy import to avoid circular dependency
        from app.repo.browser_config_repo import BrowserConfigRepo

        browser_configs = []
        for browser_config_id in browser_config_ids:
            browser_config = BrowserConfigRepo.get_by_id(db, browser_config_id)
            if not browser_config:
                raise ValueError(f"Browser config with id {browser_config_id} not found")
            if browser_config.project_id != project_id:
                raise ValueError(
                    f"Browser config {browser_config_id} does not belong to project {project_id}"
                )
            browser_configs.append(browser_config)

        return browser_configs

    @staticmethod
    def _validate_secret_values(
        db: Session, secret_value_ids: List[str], project_id: str
    ) -> List[SecretValue]:
        """
        Validate that secret value IDs exist and belong to the specified project.

        Args:
            db: Database session
            secret_value_ids: List of secret value IDs to validate
            project_id: Project ID to validate ownership

        Returns:
            List[SecretValue]: List of validated secret values

        Raises:
            ValueError: If any secret value doesn't exist or doesn't belong to project
        """
        if not secret_value_ids:
            return []

        secret_values = []
        for secret_value_id in secret_value_ids:
            secret_value = SecretValueRepo.get_by_id(db, secret_value_id)
            if not secret_value:
                raise ValueError(f"Secret value with id {secret_value_id} not found")
            if secret_value.project_id != project_id:
                raise ValueError(
                    f"Secret value {secret_value_id} does not belong to project {project_id}"
                )
            secret_values.append(secret_value)

        return secret_values

    @staticmethod
    def _associate_browser_configs_with_test_case(
        db: Session, test_case_id: str, browser_config_ids: List[str]
    ) -> None:
        """
        Associate browser configs with a test case via the association table.

        Args:
            db: Database session
            test_case_id: Test case ID to associate with
            browser_config_ids: List of browser config IDs to associate
        """
        for browser_config_id in browser_config_ids:
            association = TestCaseBrowserConfig(
                test_case_id=test_case_id, browser_config_id=browser_config_id
            )
            db.add(association)

    @staticmethod
    def _create_test_traversals_with_secrets(
        db: Session,
        test_case_id: str,
        browser_configs: List[BrowserConfig],
        secret_values: List[SecretValue],
    ) -> List[TestTraversal]:
        """
        Create test traversals for each browser config and associate secret values with test case.

        Args:
            db: Database session
            test_case_id: Test case ID to create traversals for
            browser_configs: List of browser configs to create traversals for
            secret_values: List of secret values to associate with the test case

        Returns:
            List[TestTraversal]: List of created test traversals
        """
        test_traversals = []

        # Associate all secret values with the test case
        for secret_value in secret_values:
            association = SecretValueTestCase(
                test_case_id=test_case_id,
                secret_value_id=secret_value.id,
            )
            db.add(association)

        for i, browser_config in enumerate(browser_configs):
            # Create test traversal
            traversal_name = (
                f"Traversal {i + 1} - {browser_config.browser_config.get('browser', 'Unknown')}"
            )

            test_traversal_data = CreateTestTraversal(
                test_case_id=test_case_id,
                browser_config_id=browser_config.id,
                traversal_name=traversal_name,
            )

            test_traversal = TestTraversalRepo.create(db, test_traversal_data)
            test_traversals.append(test_traversal)

        return test_traversals

    @staticmethod
    def create_with_dependencies(
        db: Session, test_case_data: CreateTestCase
    ) -> CreateTestCaseResponse:
        """
        Create a test case with all its dependencies including browser configs, secret values, and test traversals.

        Args:
            db: Database session
            test_case_data: Test case creation data with dependencies

        Returns:
            CreateTestCaseResponse: Comprehensive response with all created and associated entities

        Raises:
            ValueError: If validation fails for any dependencies
        """
        try:
            # Validate project exists
            project = ProjectRepo.get_by_id(db, test_case_data.project_id)
            if not project:
                raise ValueError(f"Project with id {test_case_data.project_id} not found")

            # Validate document exists if provided
            if test_case_data.document_id:
                document = DocumentRepo.get_by_id(db, test_case_data.document_id)
                if not document:
                    raise ValueError(f"Document with id {test_case_data.document_id} not found")

            # Validate existing browser configs
            existing_browser_configs = TestCaseRepo._validate_browser_configs(
                db, test_case_data.existing_browser_config_ids or [], test_case_data.project_id
            )

            # Validate existing secret values
            existing_secret_values = TestCaseRepo._validate_secret_values(
                db, test_case_data.existing_secret_value_ids or [], test_case_data.project_id
            )

            # Create test case
            test_case = TestCaseRepo.create(db, test_case_data)

            # Create new browser configs
            # Lazy import to avoid circular dependency
            from app.repo.browser_config_repo import BrowserConfigRepo

            created_browser_configs: List[BrowserConfig] = []
            if test_case_data.new_browser_configs:
                for browser_config_data in test_case_data.new_browser_configs:
                    # Ensure project_id matches
                    browser_config = BrowserConfigRepo.create(db, browser_config_data)
                    created_browser_configs.append(browser_config)

            # Associate existing browser configs with test case
            if existing_browser_configs:
                TestCaseRepo._associate_browser_configs_with_test_case(
                    db, test_case.id, [bc.id for bc in existing_browser_configs]
                )

            # Create new secret values
            created_secret_values: List[SecretValue] = []
            if test_case_data.new_secret_values:
                for secret_value_data in test_case_data.new_secret_values:
                    # Ensure project_id matches
                    secret_value = SecretValueRepo.create(db, secret_value_data)
                    created_secret_values.append(secret_value)

            # Combine all browser configs and secret values
            all_browser_configs = created_browser_configs + existing_browser_configs
            all_secret_values = created_secret_values + existing_secret_values

            # Create test traversals
            created_test_traversals: List[TestTraversal] = []
            if all_browser_configs:
                created_test_traversals = TestCaseRepo._create_test_traversals_with_secrets(
                    db, test_case.id, all_browser_configs, all_secret_values
                )

            # Commit all changes
            db.commit()

            # Convert to response models
            response_test_case = ResponseTestCase(
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

            response_created_browser_configs = [
                ResponseBrowserConfig(
                    id=bc.id,
                    project_id=bc.project_id,
                    browser_config=bc.browser_config,
                    created_at=bc.created_at,
                    updated_at=bc.updated_at,
                )
                for bc in created_browser_configs
            ]

            response_associated_browser_configs = [
                ResponseBrowserConfig(
                    id=bc.id,
                    project_id=bc.project_id,
                    browser_config=bc.browser_config,
                    created_at=bc.created_at,
                    updated_at=bc.updated_at,
                )
                for bc in existing_browser_configs
            ]

            response_created_secret_values = [
                ResponseSecretValue(
                    id=sv.id,
                    project_id=sv.project_id,
                    secret_name=sv.secret_name,
                    secret_value=sv.secret_value,
                    created_at=sv.created_at,
                    updated_at=sv.updated_at,
                )
                for sv in created_secret_values
            ]

            response_associated_secret_values = [
                ResponseSecretValue(
                    id=sv.id,
                    project_id=sv.project_id,
                    secret_name=sv.secret_name,
                    secret_value=sv.secret_value,
                    created_at=sv.created_at,
                    updated_at=sv.updated_at,
                )
                for sv in existing_secret_values
            ]

            response_created_test_traversals = [
                ResponseTestTraversal(
                    id=tt.id,
                    test_case_id=tt.test_case_id,
                    browser_config_id=tt.browser_config_id,
                    created_at=tt.created_at,
                    updated_at=tt.updated_at,
                    traversal_name=tt.traversal_name,
                )
                for tt in created_test_traversals
            ]

            return CreateTestCaseResponse(
                test_case=response_test_case,
                created_browser_configs=response_created_browser_configs,
                associated_browser_configs=response_associated_browser_configs,
                created_secret_values=response_created_secret_values,
                associated_secret_values=response_associated_secret_values,
                created_test_traversals=response_created_test_traversals,
            )

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_all_extended_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        project_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ExtendedResponseTestcase]:
        """
        Retrieve all test cases with extended responses, pagination, sorting, filtering, and search.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            project_id: Optional project ID to filter by (default: None - returns all test cases)
            search: Optional search term to filter by test name or description (default: None)

        Returns:
            Sequence[ExtendedResponseTestcase]: List of extended test cases sorted by creation date
        """
        # Get basic test cases with pagination and filtering
        test_cases = TestCaseRepo.get_all_with_sorting_and_filter(
            db=db,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            project_id=project_id,
            search=search,
        )

        # Convert to extended responses
        extended_test_cases = []
        for test_case in test_cases:
            extended_test_case = TestCaseRepo.get_extended_by_id(db, test_case.id)
            if extended_test_case:
                extended_test_cases.append(extended_test_case)

        return extended_test_cases

    @staticmethod
    def _handle_browser_config_associations(
        db: Session,
        test_case_id: str,
        browser_config_ids_to_add: Optional[List[str]],
        browser_config_ids_to_remove: Optional[List[str]],
        new_browser_configs: Optional[List[CreateBrowserConfig]],
        project_id: str,
    ) -> None:
        """
        Handle browser configuration associations for a test case.

        Args:
            db: Database session
            test_case_id: Test case ID to manage associations for
            browser_config_ids_to_add: Existing browser config IDs to associate
            browser_config_ids_to_remove: Browser config IDs to disassociate
            new_browser_configs: New browser configs to create and associate
            project_id: Project ID for validation
        """
        # Handle removing associations
        if browser_config_ids_to_remove:
            TestCaseRepo._remove_browser_config_associations(
                db, test_case_id, browser_config_ids_to_remove
            )

        # Handle adding associations for existing browser configs
        if browser_config_ids_to_add:
            # Validate that the browser configs exist and belong to the project
            validated_browser_configs = TestCaseRepo._validate_browser_configs(
                db, browser_config_ids_to_add, project_id
            )
            # Add associations
            TestCaseRepo._associate_browser_configs_with_test_case(
                db, test_case_id, [bc.id for bc in validated_browser_configs]
            )

        # Handle creating new browser configs and associating them
        if new_browser_configs:
            from app.repo.browser_config_repo import BrowserConfigRepo

            # Update the test_case_id for each new browser config
            for browser_config_data in new_browser_configs:
                browser_config_data.test_case_id = test_case_id

            # Create the new browser configs
            created_configs, failed_creations = BrowserConfigRepo.bulk_create_with_traversals(
                db, new_browser_configs
            )

            # Associate the successfully created configs
            if created_configs:
                TestCaseRepo._associate_browser_configs_with_test_case(
                    db, test_case_id, [bc.id for bc in created_configs]
                )

        # Commit all association changes
        db.commit()

    @staticmethod
    def _remove_browser_config_associations(
        db: Session, test_case_id: str, browser_config_ids: List[str]
    ) -> None:
        """
        Remove associations between a test case and browser configurations.

        Args:
            db: Database session
            test_case_id: Test case ID
            browser_config_ids: List of browser config IDs to disassociate
        """
        for browser_config_id in browser_config_ids:
            # Find and delete the association
            association = db.exec(
                select(TestCaseBrowserConfig).where(
                    TestCaseBrowserConfig.test_case_id == test_case_id,
                    TestCaseBrowserConfig.browser_config_id == browser_config_id,
                )
            ).first()

            if association:
                db.delete(association)

    @staticmethod
    def _handle_secret_value_associations(
        db: Session,
        test_case_id: str,
        secret_value_ids_to_add: Optional[List[str]],
        secret_value_ids_to_remove: Optional[List[str]],
        new_secret_values: Optional[List[CreateSecretValue]],
        project_id: str,
    ) -> None:
        """
        Handle secret value associations for a test case.

        Args:
            db: Database session
            test_case_id: Test case ID to manage associations for
            secret_value_ids_to_add: Existing secret value IDs to associate
            secret_value_ids_to_remove: Secret value IDs to disassociate
            new_secret_values: New secret values to create and associate
            project_id: Project ID for validation
        """
        # Handle removing associations
        if secret_value_ids_to_remove:
            TestCaseRepo._remove_secret_value_associations(
                db, test_case_id, secret_value_ids_to_remove
            )

        # Handle adding associations for existing secret values
        if secret_value_ids_to_add:
            # Validate that the secret values exist and belong to the project
            validated_secret_values = TestCaseRepo._validate_secret_values(
                db, secret_value_ids_to_add, project_id
            )
            # Add associations
            TestCaseRepo._associate_secret_values_with_test_case(
                db, test_case_id, [sv.id for sv in validated_secret_values]
            )

        # Handle creating new secret values and associating them
        if new_secret_values:
            # Update the test_case_id for each new secret value
            for secret_value_data in new_secret_values:
                secret_value_data.test_case_id = test_case_id

            # Create the new secret values
            created_secrets, failed_creations = SecretValueRepo.bulk_create(db, new_secret_values)

            # Associate the successfully created secrets
            if created_secrets:
                TestCaseRepo._associate_secret_values_with_test_case(
                    db, test_case_id, [sv.id for sv in created_secrets]
                )

        # Commit all association changes
        db.commit()

    @staticmethod
    def _remove_secret_value_associations(
        db: Session, test_case_id: str, secret_value_ids: List[str]
    ) -> None:
        """
        Remove associations between a test case and secret values.

        Args:
            db: Database session
            test_case_id: Test case ID
            secret_value_ids: List of secret value IDs to disassociate
        """
        for secret_value_id in secret_value_ids:
            # Find and delete the association
            association = db.exec(
                select(SecretValueTestCase).where(
                    SecretValueTestCase.test_case_id == test_case_id,
                    SecretValueTestCase.secret_value_id == secret_value_id,
                )
            ).first()

            if association:
                db.delete(association)

    @staticmethod
    def _associate_secret_values_with_test_case(
        db: Session, test_case_id: str, secret_value_ids: List[str]
    ) -> None:
        """
        Associate secret values with a test case via the association table.

        Args:
            db: Database session
            test_case_id: Test case ID to associate with
            secret_value_ids: List of secret value IDs to associate
        """
        for secret_value_id in secret_value_ids:
            # Check if association already exists
            existing_association = db.exec(
                select(SecretValueTestCase).where(
                    SecretValueTestCase.test_case_id == test_case_id,
                    SecretValueTestCase.secret_value_id == secret_value_id,
                )
            ).first()

            if not existing_association:
                association = SecretValueTestCase(
                    test_case_id=test_case_id, secret_value_id=secret_value_id
                )
                db.add(association)
