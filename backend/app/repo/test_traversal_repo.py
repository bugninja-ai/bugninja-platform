"""
Test Traversal Repository

This module provides static methods for CRUD operations on TestTraversal entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import List, Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

from app.db.browser_config import BrowserConfig
from app.db.test_run import TestRun
from app.db.test_traversal import TestTraversal
from app.schemas.communication.test_traversal import (
    ExtendedResponseTestTraversal,
    LightResponseTestRun,
)
from app.schemas.crud.browser_config import BrowserConfigData, ResponseBrowserConfig
from app.schemas.crud.test_traversal import (
    CreateTestTraversal,
    UpdateTestTraversal,
)


class TestTraversalRepo:
    """
    Repository class for TestTraversal entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, test_traversal_data: CreateTestTraversal) -> TestTraversal:
        """
        Create a new test traversal in the database.

        Args:
            db: Database session
            test_traversal_data: Test traversal creation data

        Returns:
            TestTraversal: The created test traversal instance
        """
        test_traversal = TestTraversal(
            id=CUID().generate(),
            test_case_id=test_traversal_data.test_case_id,
            browser_config_id=test_traversal_data.browser_config_id,
            traversal_name=test_traversal_data.traversal_name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(test_traversal)
        db.commit()
        db.refresh(test_traversal)
        return test_traversal

    @staticmethod
    def get_by_id(db: Session, test_traversal_id: str) -> Optional[TestTraversal]:
        """
        Retrieve a test traversal by its ID.

        Args:
            db: Database session
            test_traversal_id: Unique test traversal identifier

        Returns:
            Optional[TestTraversal]: The test traversal if found, None otherwise
        """
        statement = select(TestTraversal).where(TestTraversal.id == test_traversal_id)
        return db.exec(statement).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[TestTraversal]:
        """
        Retrieve all test traversals with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestTraversal]: List of test traversals
        """
        statement = select(TestTraversal).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_all_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        test_case_id: Optional[str] = None,
    ) -> Sequence[TestTraversal]:
        """
        Retrieve all test traversals with pagination, sorting, and optional test case filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            test_case_id: Optional test case ID to filter by (default: None - returns all test traversals)

        Returns:
            Sequence[TestTraversal]: List of test traversals sorted by creation date
        """
        # Calculate skip based on page and page_size
        skip = (page - 1) * page_size

        # Build the base query
        if test_case_id:
            # Filter by test case ID
            base_statement = select(TestTraversal).where(TestTraversal.test_case_id == test_case_id)
        else:
            # No filtering - get all test traversals
            base_statement = select(TestTraversal)

        # Add sorting and pagination
        if sort_order.lower() == "asc":
            statement = (
                base_statement.order_by(col(TestTraversal.created_at).asc())
                .offset(skip)
                .limit(page_size)
            )
        else:
            statement = (
                base_statement.order_by(col(TestTraversal.created_at).desc())
                .offset(skip)
                .limit(page_size)
            )

        return db.exec(statement).all()

    @staticmethod
    def get_by_test_case_id(
        db: Session, test_case_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestTraversal]:
        """
        Retrieve all test traversals for a specific test case.

        Args:
            db: Database session
            test_case_id: Test case identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestTraversal]: List of test traversals for the test case
        """
        statement = (
            select(TestTraversal)
            .where(TestTraversal.test_case_id == test_case_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_browser_config_id(
        db: Session, browser_config_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestTraversal]:
        """
        Retrieve all test traversals for a specific browser configuration.

        Args:
            db: Database session
            browser_config_id: Browser configuration identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestTraversal]: List of test traversals for the browser configuration
        """
        statement = (
            select(TestTraversal)
            .where(TestTraversal.browser_config_id == browser_config_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(
        db: Session, test_traversal_id: str, test_traversal_data: UpdateTestTraversal
    ) -> Optional[TestTraversal]:
        """
        Update an existing test traversal.

        Args:
            db: Database session
            test_traversal_id: Unique test traversal identifier
            test_traversal_data: Test traversal update data

        Returns:
            Optional[TestTraversal]: The updated test traversal if found, None otherwise
        """
        test_traversal = TestTraversalRepo.get_by_id(db, test_traversal_id)
        if not test_traversal:
            return None

        for k, v in test_traversal_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(test_traversal, k, v)

        test_traversal.updated_at = datetime.now(timezone.utc)

        db.add(test_traversal)
        db.commit()
        db.refresh(test_traversal)
        return test_traversal

    @staticmethod
    def delete(db: Session, test_traversal_id: str) -> bool:
        """
        Delete a test traversal by its ID.

        Args:
            db: Database session
            test_traversal_id: Unique test traversal identifier

        Returns:
            bool: True if test traversal was deleted, False if not found
        """
        test_traversal = TestTraversalRepo.get_by_id(db, test_traversal_id)
        if not test_traversal:
            return False

        db.delete(test_traversal)
        db.commit()
        return True

    @staticmethod
    def get_by_name(db: Session, traversal_name: str) -> Optional[TestTraversal]:
        """
        Retrieve a test traversal by its name.

        Args:
            db: Database session
            traversal_name: Test traversal name

        Returns:
            Optional[TestTraversal]: The test traversal if found, None otherwise
        """
        statement = select(TestTraversal).where(TestTraversal.traversal_name == traversal_name)
        return db.exec(statement).first()

    @staticmethod
    def search_by_name(
        db: Session, name_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[TestTraversal]:
        """
        Search test traversals by name pattern.

        Args:
            db: Database session
            name_pattern: Name pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[TestTraversal]: List of matching test traversals
        """
        statement = (
            select(TestTraversal)
            .where(col(TestTraversal.traversal_name).ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_test_case_and_browser_config(
        db: Session, test_case_id: str, browser_config_id: str
    ) -> Optional[TestTraversal]:
        """
        Retrieve a test traversal by test case and browser configuration combination.

        Args:
            db: Database session
            test_case_id: Test case identifier
            browser_config_id: Browser configuration identifier

        Returns:
            Optional[TestTraversal]: The test traversal if found, None otherwise
        """
        statement = select(TestTraversal).where(
            TestTraversal.test_case_id == test_case_id,
            TestTraversal.browser_config_id == browser_config_id,
        )
        return db.exec(statement).first()

    @staticmethod
    def count_by_test_case(db: Session, test_case_id: str) -> int:
        """
        Get the total number of test traversals for a test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            int: Total number of test traversals for the test case
        """
        statement = select(TestTraversal).where(TestTraversal.test_case_id == test_case_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of test traversals.

        Args:
            db: Database session

        Returns:
            int: Total number of test traversals
        """
        statement = select(TestTraversal)
        return len(db.exec(statement).all())

    @staticmethod
    def count_with_filter(db: Session, test_case_id: Optional[str] = None) -> int:
        """
        Get the total number of test traversals with optional test case filtering.

        Args:
            db: Database session
            test_case_id: Optional test case ID to filter by (default: None - counts all test traversals)

        Returns:
            int: Total number of test traversals matching the filter
        """
        if test_case_id:
            statement = select(TestTraversal.id).where(TestTraversal.test_case_id == test_case_id)
        else:
            statement = select(TestTraversal.id)

        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_test_case(db: Session, test_case_id: str) -> int:
        """
        Delete all test traversals for a specific test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            int: Number of test traversals deleted
        """
        statement = select(TestTraversal).where(TestTraversal.test_case_id == test_case_id)
        test_traversals = db.exec(statement).all()
        count = len(test_traversals)

        for test_traversal in test_traversals:
            db.delete(test_traversal)

        db.commit()
        return count

    # Extended Response Methods

    @staticmethod
    def get_extended_by_id(
        db: Session, test_traversal_id: str
    ) -> Optional[ExtendedResponseTestTraversal]:
        """
        Retrieve an extended test traversal response with nested browser config, latest run, and secret values.

        Args:
            db: Database session
            test_traversal_id: Unique test traversal identifier

        Returns:
            Optional[ExtendedResponseTestTraversal]: The extended test traversal response if found, None otherwise
        """
        # Get the test traversal
        test_traversal = TestTraversalRepo.get_by_id(db, test_traversal_id)
        if not test_traversal:
            return None

        # Get associated browser config
        browser_config_statement = select(BrowserConfig).where(
            BrowserConfig.id == test_traversal.browser_config_id
        )
        browser_config = db.exec(browser_config_statement).first()

        if not browser_config:
            return None  # Browser config is required for extended response

        # Convert browser config to ResponseBrowserConfig
        response_browser_config = ResponseBrowserConfig(
            id=browser_config.id,
            project_id=browser_config.project_id,
            browser_config=BrowserConfigData.model_validate(browser_config.browser_config),
            created_at=browser_config.created_at,
            updated_at=browser_config.updated_at,
        )

        # Get latest test run
        latest_run_statement = (
            select(TestRun)
            .where(TestRun.test_traversal_id == test_traversal_id)
            .order_by(col(TestRun.started_at).desc())
        )
        latest_run = db.exec(latest_run_statement).first()

        # Convert latest run to LightResponseTestRun
        light_latest_run = None
        if latest_run:
            light_latest_run = LightResponseTestRun(
                id=latest_run.id,
                state=latest_run.current_state,
                finished_at=latest_run.finished_at,
            )

        return ExtendedResponseTestTraversal(
            id=test_traversal.id,
            created_at=test_traversal.created_at,
            updated_at=test_traversal.updated_at,
            traversal_name=test_traversal.traversal_name,
            browser_config=response_browser_config,
            latest_run=light_latest_run,
        )

    @staticmethod
    def get_extended_by_test_case_id(
        db: Session, test_case_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[ExtendedResponseTestTraversal]:
        """
        Retrieve all extended test traversals for a specific test case.

        Args:
            db: Database session
            test_case_id: Test case identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[ExtendedResponseTestTraversal]: List of extended test traversal responses
        """
        test_traversals = TestTraversalRepo.get_by_test_case_id(db, test_case_id, skip, limit)
        extended_test_traversals = []

        for test_traversal in test_traversals:
            extended_test_traversal = TestTraversalRepo.get_extended_by_id(db, test_traversal.id)
            if extended_test_traversal:
                extended_test_traversals.append(extended_test_traversal)

        return extended_test_traversals

    @staticmethod
    def get_all_extended_with_sorting_and_filter(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        sort_order: str = "desc",
        test_case_id: Optional[str] = None,
    ) -> List[ExtendedResponseTestTraversal]:
        """
        Retrieve all test traversals with extended responses, pagination, sorting, and optional test case filtering.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")
            test_case_id: Optional test case ID to filter by (default: None - returns all test traversals)

        Returns:
            List[ExtendedResponseTestTraversal]: List of extended test traversals sorted by creation date
        """
        # Get basic test traversals with pagination and filtering
        test_traversals = TestTraversalRepo.get_all_with_sorting_and_filter(
            db=db,
            page=page,
            page_size=page_size,
            sort_order=sort_order,
            test_case_id=test_case_id,
        )

        # Convert to extended responses
        extended_test_traversals = []
        for test_traversal in test_traversals:
            extended_test_traversal = TestTraversalRepo.get_extended_by_id(db, test_traversal.id)
            if extended_test_traversal:
                extended_test_traversals.append(extended_test_traversal)

        return extended_test_traversals

    @staticmethod
    def get_all_extended(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[ExtendedResponseTestTraversal]:
        """
        Retrieve all test traversals with extended responses including browser config, latest run, and secret values.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[ExtendedResponseTestTraversal]: List of extended test traversal responses
        """
        test_traversals = TestTraversalRepo.get_all(db, skip, limit)
        extended_test_traversals = []

        for test_traversal in test_traversals:
            extended_test_traversal = TestTraversalRepo.get_extended_by_id(db, test_traversal.id)
            if extended_test_traversal:
                extended_test_traversals.append(extended_test_traversal)

        return extended_test_traversals
