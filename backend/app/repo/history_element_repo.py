"""
History Element Repository

This module provides static methods for CRUD operations on HistoryElement entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime
from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

from app.db.history_element import HistoryElement, HistoryElementState
from app.schemas.crud.history_element import (
    CreateHistoryElement,
    UpdateHistoryElement,
)


class HistoryElementRepo:
    """
    Repository class for HistoryElement entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, history_element_data: CreateHistoryElement) -> HistoryElement:
        """
        Create a new history element in the database.

        Args:
            db: Database session
            history_element_data: History element creation data

        Returns:
            HistoryElement: The created history element instance
        """
        history_element = HistoryElement(
            id=CUID().generate(),
            test_run_id=history_element_data.test_run_id,
            action_id=history_element_data.action_id,
            history_element_state=history_element_data.history_element_state,
            screenshot=history_element_data.screenshot,
        )
        db.add(history_element)
        db.commit()
        db.refresh(history_element)
        return history_element

    @staticmethod
    def get_by_id(db: Session, history_element_id: str) -> Optional[HistoryElement]:
        """
        Retrieve a history element by its ID.

        Args:
            db: Database session
            history_element_id: Unique history element identifier

        Returns:
            Optional[HistoryElement]: The history element if found, None otherwise
        """
        statement = select(HistoryElement).where(HistoryElement.id == history_element_id)
        return db.exec(statement).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[HistoryElement]:
        """
        Retrieve all history elements with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of history elements
        """
        statement = select(HistoryElement).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_test_run_id(
        db: Session, test_run_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[HistoryElement]:
        """
        Retrieve all history elements for a specific test run.

        Args:
            db: Database session
            test_run_id: Test run identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of history elements for the test run
        """
        statement = (
            select(HistoryElement)
            .where(HistoryElement.test_run_id == test_run_id)
            .order_by(col(HistoryElement.action_started_at))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_action_id(
        db: Session, action_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[HistoryElement]:
        """
        Retrieve all history elements for a specific action.

        Args:
            db: Database session
            action_id: Action identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of history elements for the action
        """
        statement = (
            select(HistoryElement)
            .where(HistoryElement.action_id == action_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_state(
        db: Session, state: HistoryElementState, skip: int = 0, limit: int = 100
    ) -> Sequence[HistoryElement]:
        """
        Retrieve all history elements with a specific state.

        Args:
            db: Database session
            state: History element state to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of history elements with the specified state
        """
        statement = (
            select(HistoryElement)
            .where(HistoryElement.history_element_state == state)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_passed_elements(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[HistoryElement]:
        """
        Retrieve all passed history elements.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of passed history elements
        """
        statement = (
            select(HistoryElement)
            .where(HistoryElement.history_element_state == HistoryElementState.PASSED)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_failed_elements(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[HistoryElement]:
        """
        Retrieve all failed history elements.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of failed history elements
        """
        statement = (
            select(HistoryElement)
            .where(HistoryElement.history_element_state == HistoryElementState.FAILED)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(
        db: Session, history_element_id: str, history_element_data: UpdateHistoryElement
    ) -> Optional[HistoryElement]:
        """
        Update an existing history element.

        Args:
            db: Database session
            history_element_id: Unique history element identifier
            history_element_data: History element update data

        Returns:
            Optional[HistoryElement]: The updated history element if found, None otherwise
        """
        history_element = HistoryElementRepo.get_by_id(db, history_element_id)
        if not history_element:
            return None

        for k, v in history_element_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(history_element, k, v)

        db.add(history_element)
        db.commit()
        db.refresh(history_element)
        return history_element

    @staticmethod
    def delete(db: Session, history_element_id: str) -> bool:
        """
        Delete a history element by its ID.

        Args:
            db: Database session
            history_element_id: Unique history element identifier

        Returns:
            bool: True if history element was deleted, False if not found
        """
        history_element = HistoryElementRepo.get_by_id(db, history_element_id)
        if not history_element:
            return False

        db.delete(history_element)
        db.commit()
        return True

    @staticmethod
    def get_by_time_range(
        db: Session, test_run_id: str, start_time: datetime, end_time: datetime
    ) -> Sequence[HistoryElement]:
        """
        Retrieve history elements within a specific time range for a test run.

        Args:
            db: Database session
            test_run_id: Test run identifier
            start_time: Start time for the range
            end_time: End time for the range

        Returns:
            Sequence[HistoryElement]: List of history elements within the time range
        """
        statement = (
            select(HistoryElement)
            .where(
                HistoryElement.test_run_id == test_run_id,
                HistoryElement.action_started_at >= start_time,
                HistoryElement.action_started_at <= end_time,
            )
            .order_by(col(HistoryElement.action_started_at))
        )
        return db.exec(statement).all()

    @staticmethod
    def get_with_screenshots(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[HistoryElement]:
        """
        Retrieve history elements that have screenshots.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[HistoryElement]: List of history elements with screenshots
        """
        statement = (
            select(HistoryElement)
            .where(col(HistoryElement.screenshot).is_not(None))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def count_by_test_run(db: Session, test_run_id: str) -> int:
        """
        Get the total number of history elements for a test run.

        Args:
            db: Database session
            test_run_id: Test run identifier

        Returns:
            int: Total number of history elements for the test run
        """
        statement = select(HistoryElement).where(HistoryElement.test_run_id == test_run_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count_by_state(db: Session, state: HistoryElementState) -> int:
        """
        Get the total number of history elements with a specific state.

        Args:
            db: Database session
            state: History element state to count

        Returns:
            int: Total number of history elements with the specified state
        """
        statement = select(HistoryElement).where(HistoryElement.history_element_state == state)
        return len(db.exec(statement).all())

    @staticmethod
    def count_passed_by_test_run(db: Session, test_run_id: str) -> int:
        """
        Get the total number of passed history elements for a test run.

        Args:
            db: Database session
            test_run_id: Test run identifier

        Returns:
            int: Total number of passed history elements for the test run
        """
        statement = select(HistoryElement).where(
            HistoryElement.test_run_id == test_run_id,
            HistoryElement.history_element_state == HistoryElementState.PASSED,
        )
        return len(db.exec(statement).all())

    @staticmethod
    def count_failed_by_test_run(db: Session, test_run_id: str) -> int:
        """
        Get the total number of failed history elements for a test run.

        Args:
            db: Database session
            test_run_id: Test run identifier

        Returns:
            int: Total number of failed history elements for the test run
        """
        statement = select(HistoryElement).where(
            HistoryElement.test_run_id == test_run_id,
            HistoryElement.history_element_state == HistoryElementState.FAILED,
        )
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of history elements.

        Args:
            db: Database session

        Returns:
            int: Total number of history elements
        """
        statement = select(HistoryElement)
        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_test_run(db: Session, test_run_id: str) -> int:
        """
        Delete all history elements for a specific test run.

        Args:
            db: Database session
            test_run_id: Test run identifier

        Returns:
            int: Number of history elements deleted
        """
        statement = select(HistoryElement).where(HistoryElement.test_run_id == test_run_id)
        history_elements = db.exec(statement).all()
        count = len(history_elements)

        for history_element in history_elements:
            db.delete(history_element)

        db.commit()
        return count

    @staticmethod
    def delete_by_action(db: Session, action_id: str) -> int:
        """
        Delete all history elements for a specific action.

        Args:
            db: Database session
            action_id: Action identifier

        Returns:
            int: Number of history elements deleted
        """
        statement = select(HistoryElement).where(HistoryElement.action_id == action_id)
        history_elements = db.exec(statement).all()
        count = len(history_elements)

        for history_element in history_elements:
            db.delete(history_element)

        db.commit()
        return count
