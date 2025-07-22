"""
Test Run Repository

This module provides static methods for CRUD operations on TestRun entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import List, Optional, Sequence

from sqlmodel import Session, col, select

from app.db.test_run import RunOrigin, RunState, RunType, TestRun
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
            id=test_run_data.id,
            test_traversal_id=test_run_data.test_traversal_id,
            browser_config_id=test_run_data.browser_config_id,
            run_type=test_run_data.run_type,
            origin=test_run_data.origin,
            repair_was_needed=test_run_data.repair_was_needed,
            started_at=test_run_data.started_at,
            finished_at=test_run_data.finished_at,
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
