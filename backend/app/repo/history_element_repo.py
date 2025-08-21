"""
History Element Repository

This module provides static methods for CRUD operations on HistoryElement entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, delete, select

from app.db.history_element import HistoryElement
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
    def delete_all(db: Session) -> bool:
        db.exec(delete(HistoryElement))  # type: ignore
        db.commit()
        return True

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
