"""
Action Repository

This module provides static methods for CRUD operations on Action entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, delete, select

from app.db.action import Action
from app.schemas.crud.action import CreateAction, UpdateAction


class ActionRepo:
    """
    Repository class for Action entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, action_data: CreateAction) -> Action:
        """
        Create a new action in the database.

        Args:
            db: Database session
            action_data: Action creation data

        Returns:
            Action: The created action instance
        """
        action = Action(
            id=CUID().generate(),
            brain_state_id=action_data.brain_state_id,
            idx_in_brain_state=action_data.idx_in_brain_state,
            action=action_data.action,
            dom_element_data=action_data.dom_element_data,
            valid=action_data.valid,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def get_by_id(db: Session, action_id: str) -> Optional[Action]:
        """
        Retrieve an action by its ID.

        Args:
            db: Database session
            action_id: Unique action identifier

        Returns:
            Optional[Action]: The action if found, None otherwise
        """
        statement = select(Action).where(Action.id == action_id)
        return db.exec(statement).first()

    @staticmethod
    def get_by_brain_state_id(
        db: Session, brain_state_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Action]:
        """
        Retrieve all actions for a specific brain state.

        Args:
            db: Database session
            brain_state_id: Brain state identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Action]: List of actions for the brain state
        """
        statement = (
            select(Action)
            .where(Action.brain_state_id == brain_state_id)
            .order_by(col(Action.idx_in_brain_state))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(db: Session, action_id: str, action_data: UpdateAction) -> Optional[Action]:
        """
        Update an existing action.

        Args:
            db: Database session
            action_id: Unique action identifier
            action_data: Action update data

        Returns:
            Optional[Action]: The updated action if found, None otherwise
        """
        action = ActionRepo.get_by_id(db, action_id)
        if not action:
            return None

        for k, v in action_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(action, k, v)

        action.updated_at = datetime.now(timezone.utc)

        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def delete(db: Session, action_id: str) -> bool:
        """
        Delete an action by its ID.

        Args:
            db: Database session
            action_id: Unique action identifier

        Returns:
            bool: True if action was deleted, False if not found
        """
        action = ActionRepo.get_by_id(db, action_id)
        if not action:
            return False

        db.delete(action)
        db.commit()
        return True

    @staticmethod
    def delete_all(db: Session) -> bool:
        """
        Delete every action in the database.

        Returns:
            bool: True if every action was deleted, False if not found
        """
        db.exec(delete(Action))  # type: ignore
        db.commit()
        return True
