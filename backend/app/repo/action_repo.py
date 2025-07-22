"""
Action Repository

This module provides static methods for CRUD operations on Action entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

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
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Action]:
        """
        Retrieve all actions with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Action]: List of actions
        """
        statement = select(Action).offset(skip).limit(limit)
        return db.exec(statement).all()

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
    def get_valid_actions(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Action]:
        """
        Retrieve all valid actions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Action]: List of valid actions
        """
        statement = select(Action).where(Action.valid).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_invalid_actions(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Action]:
        """
        Retrieve all invalid actions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Action]: List of invalid actions
        """
        statement = select(Action).where(not Action.valid).offset(skip).limit(limit)
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
    def get_by_index_in_brain_state(db: Session, brain_state_id: str, idx: int) -> Optional[Action]:
        """
        Retrieve an action by its index within a brain state.

        Args:
            db: Database session
            brain_state_id: Brain state identifier
            idx: Index within the brain state

        Returns:
            Optional[Action]: The action if found, None otherwise
        """
        statement = select(Action).where(
            Action.brain_state_id == brain_state_id, Action.idx_in_brain_state == idx
        )
        return db.exec(statement).first()

    @staticmethod
    def search_by_action_type(
        db: Session, action_type: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Action]:
        """
        Search actions by action type.

        Args:
            db: Database session
            action_type: Action type to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Action]: List of matching actions
        """
        # Note: This is a simplified search. For more complex JSON queries,
        # you might need to use database-specific JSON operators
        statement = (
            select(Action)
            .where(col(Action.action).contains({"type": action_type}))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def count_by_brain_state(db: Session, brain_state_id: str) -> int:
        """
        Get the total number of actions for a brain state.

        Args:
            db: Database session
            brain_state_id: Brain state identifier

        Returns:
            int: Total number of actions for the brain state
        """
        statement = select(Action).where(Action.brain_state_id == brain_state_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count_valid_by_brain_state(db: Session, brain_state_id: str) -> int:
        """
        Get the total number of valid actions for a brain state.

        Args:
            db: Database session
            brain_state_id: Brain state identifier

        Returns:
            int: Total number of valid actions for the brain state
        """
        statement = select(Action).where(Action.brain_state_id == brain_state_id, Action.valid)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of actions.

        Args:
            db: Database session

        Returns:
            int: Total number of actions
        """
        statement = select(Action)
        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_brain_state(db: Session, brain_state_id: str) -> int:
        """
        Delete all actions for a specific brain state.

        Args:
            db: Database session
            brain_state_id: Brain state identifier

        Returns:
            int: Number of actions deleted
        """
        statement = select(Action).where(Action.brain_state_id == brain_state_id)
        actions = db.exec(statement).all()
        count = len(actions)

        for action in actions:
            db.delete(action)

        db.commit()
        return count

    @staticmethod
    def get_actions_by_dom_element(
        db: Session, element_selector: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Action]:
        """
        Retrieve actions that target a specific DOM element.

        Args:
            db: Database session
            element_selector: DOM element selector to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Action]: List of actions targeting the specified DOM element
        """
        # Note: This is a simplified search. For more complex JSON queries,
        # you might need to use database-specific JSON operators
        statement = (
            select(Action)
            .where(col(Action.dom_element_data).contains({"selector": element_selector}))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()
