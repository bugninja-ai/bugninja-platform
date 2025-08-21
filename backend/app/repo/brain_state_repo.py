"""
Brain State Repository

This module provides static methods for CRUD operations on BrainState entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, delete, select

from app.db.brain_state import BrainState
from app.schemas.crud.brain_state import CreateBrainState, UpdateBrainState


class BrainStateRepo:
    """
    Repository class for BrainState entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, brain_state_data: CreateBrainState) -> BrainState:
        """
        Create a new brain state in the database.

        Args:
            db: Database session
            brain_state_data: Brain state creation data

        Returns:
            BrainState: The created brain state instance
        """
        brain_state = BrainState(
            id=CUID().generate(),
            test_traversal_id=brain_state_data.test_traversal_id,
            idx_in_run=brain_state_data.idx_in_run,
            valid=brain_state_data.valid,
            evaluation_previous_goal=brain_state_data.evaluation_previous_goal,
            memory=brain_state_data.memory,
            next_goal=brain_state_data.next_goal,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(brain_state)
        db.commit()
        db.refresh(brain_state)
        return brain_state

    @staticmethod
    def get_by_id(db: Session, brain_state_id: str) -> Optional[BrainState]:
        """
        Retrieve a brain state by its ID.

        Args:
            db: Database session
            brain_state_id: Unique brain state identifier

        Returns:
            Optional[BrainState]: The brain state if found, None otherwise
        """
        statement = select(BrainState).where(BrainState.id == brain_state_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_all(db: Session) -> bool:
        db.exec(delete(BrainState))  # type: ignore
        db.commit()
        return True

    @staticmethod
    def get_by_test_traversal_id(
        db: Session, test_traversal_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[BrainState]:
        """
        Retrieve all brain states for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrainState]: List of brain states for the test traversal
        """
        statement = (
            select(BrainState)
            .where(BrainState.test_traversal_id == test_traversal_id)
            .order_by(col(BrainState.idx_in_run))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_number_of_brainstates_for_test_traversal(db: Session, test_traversal_id: str) -> int:
        statement = select(BrainState.id).where(BrainState.test_traversal_id == test_traversal_id)
        return len(db.exec(statement).all())

    @staticmethod
    def update(
        db: Session, brain_state_id: str, brain_state_data: UpdateBrainState
    ) -> Optional[BrainState]:
        """
        Update an existing brain state.

        Args:
            db: Database session
            brain_state_id: Unique brain state identifier
            brain_state_data: Brain state update data

        Returns:
            Optional[BrainState]: The updated brain state if found, None otherwise
        """
        brain_state = BrainStateRepo.get_by_id(db, brain_state_id)
        if not brain_state:
            return None

        for k, v in brain_state_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(brain_state, k, v)

        brain_state.updated_at = datetime.now(timezone.utc)

        db.add(brain_state)
        db.commit()
        db.refresh(brain_state)
        return brain_state

    @staticmethod
    def delete(db: Session, brain_state_id: str) -> bool:
        """
        Delete a brain state by its ID.

        Args:
            db: Database session
            brain_state_id: Unique brain state identifier

        Returns:
            bool: True if brain state was deleted, False if not found
        """
        brain_state = BrainStateRepo.get_by_id(db, brain_state_id)
        if not brain_state:
            return False

        db.delete(brain_state)
        db.commit()
        return True
