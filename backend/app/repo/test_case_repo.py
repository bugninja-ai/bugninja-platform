"""
Test Case Repository

This module provides static methods for CRUD operations on TestCase entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import List, Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

from app.db.browser_config import BrowserConfig
from app.db.document import Document
from app.db.secret_value import SecretValue
from app.db.secret_value_test_traversal import SecretValueTestTraversal
from app.db.test_case import TestCase
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_traversal import TestTraversal
from app.repo.browser_config_repo import BrowserConfigRepo
from app.repo.document_repo import DocumentRepo
from app.repo.project_repo import ProjectRepo
from app.repo.secret_value_repo import SecretValueRepo
from app.repo.test_traversal_repo import TestTraversalRepo
from app.schemas.communication.test_case import ExtendedResponseTestcase
from app.schemas.crud.browser_config import ResponseBrowserConfig
from app.schemas.crud.document import ResponseDocument
from app.schemas.crud.secret_value import ResponseSecretValue
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
    def create(db: Session, test_case_data: CreateTestCase) -> TestCase:
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
        test_case_number = existing_test_cases_count + 1
        generated_cuid = CUID().generate()
        test_case_id = f"{project.name}-TC-{test_case_number}-{generated_cuid}"

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
    ) -> Sequence[TestCase]:
        """
        Retrieve all test cases with pagination, sorting, and optional project filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            project_id: Optional project ID to filter by (default: None - returns all test cases)

        Returns:
            Sequence[TestCase]: List of test cases sorted by creation date
        """
        # Calculate skip based on page and page_size
        skip = (page - 1) * page_size

        # Build the base query
        if project_id:
            # Filter by project ID
            base_statement = select(TestCase).where(TestCase.project_id == project_id)
        else:
            # No filtering - get all test cases
            base_statement = select(TestCase)

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
    def get_by_document_id(db: Session, document_id: str) -> Optional[TestCase]:
        """
        Retrieve a test case by its associated document ID.

        Args:
            db: Database session
            document_id: Document identifier

        Returns:
            Optional[TestCase]: The test case if found, None otherwise
        """
        statement = select(TestCase).where(TestCase.document_id == document_id)
        return db.exec(statement).first()

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

        for k, v in test_case_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(test_case, k, v)

        test_case.updated_at = datetime.now(timezone.utc)

        db.add(test_case)
        db.commit()
        db.refresh(test_case)
        return test_case

    @staticmethod
    def delete(db: Session, test_case_id: str) -> bool:
        """
        Delete a test case by its ID.

        Args:
            db: Database session
            test_case_id: Unique test case identifier

        Returns:
            bool: True if test case was deleted, False if not found
        """
        test_case = TestCaseRepo.get_by_id(db, test_case_id)
        if not test_case:
            return False

        db.delete(test_case)
        db.commit()
        return True

    @staticmethod
    def get_by_name(db: Session, test_name: str) -> Optional[TestCase]:
        """
        Retrieve a test case by its name.

        Args:
            db: Database session
            test_name: Test case name

        Returns:
            Optional[TestCase]: The test case if found, None otherwise
        """
        statement = select(TestCase).where(TestCase.test_name == test_name)
        return db.exec(statement).first()

    @staticmethod
    def search_by_name(
        db: Session, name_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestCase]:
        """
        Search test cases by name pattern.

        Args:
            db: Database session
            name_pattern: Name pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestCase]: List of matching test cases
        """
        statement = (
            select(TestCase)
            .where(col(TestCase.test_name).ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def search_by_description(
        db: Session, description_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestCase]:
        """
        Search test cases by description pattern.

        Args:
            db: Database session
            description_pattern: Description pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestCase]: List of matching test cases
        """
        statement = (
            select(TestCase)
            .where(col(TestCase.test_description).ilike(f"%{description_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_url_route(db: Session, url_route: str) -> Sequence[TestCase]:
        """
        Retrieve test cases by URL route.

        Args:
            db: Database session
            url_route: URL route to search for

        Returns:
            Sequence[TestCase]: List of test cases with matching URL route
        """
        statement = select(TestCase).where(TestCase.url_route == url_route)
        return db.exec(statement).all()

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
    def count_with_filter(db: Session, project_id: Optional[str] = None) -> int:
        """
        Get the total number of test cases with optional project filtering.

        Args:
            db: Database session
            project_id: Optional project ID to filter by (default: None - counts all test cases)

        Returns:
            int: Total number of test cases matching the filter
        """
        if project_id:
            statement = select(TestCase.id).where(TestCase.project_id == project_id)
        else:
            statement = select(TestCase.id)

        return len(db.exec(statement).all())

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

        # Get associated secrets through test traversals
        secrets = TestCaseRepo._get_secrets_by_test_case_id(db, test_case_id)

        # Calculate execution statistics
        execution_stats = TestCaseRepo._calculate_execution_statistics(db, test_case_id)

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
        )

    @staticmethod
    def _get_secrets_by_test_case_id(db: Session, test_case_id: str) -> List[ResponseSecretValue]:
        """
        Retrieve all secrets associated with a test case through its test traversals.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            List[ResponseSecretValue]: List of secret values associated with the test case
        """
        # Get all test traversals for this test case
        traversal_statement = select(TestTraversal).where(
            TestTraversal.test_case_id == test_case_id
        )
        test_traversals = db.exec(traversal_statement).all()

        if not test_traversals:
            return []

        # Get all unique secret values associated with these traversals
        traversal_ids = [traversal.id for traversal in test_traversals]

        secret_statement = (
            select(SecretValue)
            .join(SecretValueTestTraversal)
            .where(
                SecretValue.id == SecretValueTestTraversal.secret_value_id,
                SecretValueTestTraversal.test_traversal_id.in_(traversal_ids),
            )
            .distinct()
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
    def _calculate_execution_statistics(db: Session, test_case_id: str) -> dict:
        """
        Calculate execution statistics for a test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            dict: Dictionary containing execution statistics
        """
        from app.db.test_run import TestRun, RunState

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
        Create test traversals for each browser config and associate all secret values.

        Args:
            db: Database session
            test_case_id: Test case ID to create traversals for
            browser_configs: List of browser configs to create traversals for
            secret_values: List of secret values to associate with each traversal

        Returns:
            List[TestTraversal]: List of created test traversals
        """
        test_traversals = []

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

            # Associate all secret values with this traversal
            for secret_value in secret_values:
                association = SecretValueTestTraversal(
                    secret_value_id=secret_value.id,
                    test_traversal_id=test_traversal.id,
                )
                db.add(association)

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
            created_browser_configs = []
            if test_case_data.new_browser_configs:
                for browser_config_data in test_case_data.new_browser_configs:
                    # Ensure project_id matches
                    browser_config_data.project_id = test_case_data.project_id
                    browser_config = BrowserConfigRepo.create(db, browser_config_data)
                    created_browser_configs.append(browser_config)

            # Associate existing browser configs with test case
            if existing_browser_configs:
                TestCaseRepo._associate_browser_configs_with_test_case(
                    db, test_case.id, [bc.id for bc in existing_browser_configs]
                )

            # Create new secret values
            created_secret_values = []
            if test_case_data.new_secret_values:
                for secret_value_data in test_case_data.new_secret_values:
                    # Ensure project_id matches
                    secret_value_data.project_id = test_case_data.project_id
                    secret_value = SecretValueRepo.create(db, secret_value_data)
                    created_secret_values.append(secret_value)

            # Combine all browser configs and secret values
            all_browser_configs = created_browser_configs + existing_browser_configs
            all_secret_values = created_secret_values + existing_secret_values

            # Create test traversals
            created_test_traversals = []
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
    ) -> List[ExtendedResponseTestcase]:
        """
        Retrieve all test cases with extended responses, pagination, sorting, and optional project filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            project_id: Optional project ID to filter by (default: None - returns all test cases)

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
        )

        # Convert to extended responses
        extended_test_cases = []
        for test_case in test_cases:
            extended_test_case = TestCaseRepo.get_extended_by_id(db, test_case.id)
            if extended_test_case:
                extended_test_cases.append(extended_test_case)

        return extended_test_cases
