"""
Brain State Repository

This module provides static methods for CRUD operations on BrainState entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlmodel import Session, col, select

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
            id=brain_state_data.id,
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
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[BrainState]:
        """
        Retrieve all brain states with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrainState]: List of brain states
        """
        statement = select(BrainState).offset(skip).limit(limit)
        return db.exec(statement).all()

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
    def get_valid_brain_states(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[BrainState]:
        """
        Retrieve all valid brain states.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrainState]: List of valid brain states
        """
        statement = select(BrainState).where(BrainState.valid).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_invalid_brain_states(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[BrainState]:
        """
        Retrieve all invalid brain states.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrainState]: List of invalid brain states
        """
        statement = select(BrainState).where(not BrainState.valid).offset(skip).limit(limit)
        return db.exec(statement).all()

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

    @staticmethod
    def get_by_index_in_run(db: Session, test_traversal_id: str, idx: int) -> Optional[BrainState]:
        """
        Retrieve a brain state by its index within a test run.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier
            idx: Index within the test run

        Returns:
            Optional[BrainState]: The brain state if found, None otherwise
        """
        statement = select(BrainState).where(
            BrainState.test_traversal_id == test_traversal_id, BrainState.idx_in_run == idx
        )
        return db.exec(statement).first()

    @staticmethod
    def search_by_goal(
        db: Session, goal_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[BrainState]:
        """
        Search brain states by goal pattern.

        Args:
            db: Database session
            goal_pattern: Goal pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrainState]: List of matching brain states
        """
        statement = (
            select(BrainState)
            .where(col(BrainState.next_goal).ilike(f"%{goal_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def search_by_memory(
        db: Session, memory_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[BrainState]:
        """
        Search brain states by memory pattern.

        Args:
            db: Database session
            memory_pattern: Memory pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrainState]: List of matching brain states
        """
        statement = (
            select(BrainState)
            .where(col(BrainState.memory).ilike(f"%{memory_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def count_by_test_traversal(db: Session, test_traversal_id: str) -> int:
        """
        Get the total number of brain states for a test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            int: Total number of brain states for the test traversal
        """
        statement = select(BrainState).where(BrainState.test_traversal_id == test_traversal_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count_valid_by_test_traversal(db: Session, test_traversal_id: str) -> int:
        """
        Get the total number of valid brain states for a test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            int: Total number of valid brain states for the test traversal
        """
        statement = select(BrainState).where(
            BrainState.test_traversal_id == test_traversal_id, BrainState.valid
        )
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of brain states.

        Args:
            db: Database session

        Returns:
            int: Total number of brain states
        """
        statement = select(BrainState)
        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_test_traversal(db: Session, test_traversal_id: str) -> int:
        """
        Delete all brain states for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            int: Number of brain states deleted
        """
        statement = select(BrainState).where(BrainState.test_traversal_id == test_traversal_id)
        brain_states = db.exec(statement).all()
        count = len(brain_states)

        for brain_state in brain_states:
            db.delete(brain_state)

        db.commit()
        return count

    @staticmethod
    def get_latest_by_test_traversal(db: Session, test_traversal_id: str) -> Optional[BrainState]:
        """
        Get the latest brain state for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            Optional[BrainState]: The latest brain state if found, None otherwise
        """
        statement = (
            select(BrainState)
            .where(BrainState.test_traversal_id == test_traversal_id)
            .order_by(col(BrainState.idx_in_run).desc())
        )
        return db.exec(statement).first()

    @staticmethod
    def get_first_by_test_traversal(db: Session, test_traversal_id: str) -> Optional[BrainState]:
        """
        Get the first brain state for a specific test traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            Optional[BrainState]: The first brain state if found, None otherwise
        """
        statement = (
            select(BrainState)
            .where(BrainState.test_traversal_id == test_traversal_id)
            .order_by(col(BrainState.idx_in_run))
        )
        return db.exec(statement).first()
