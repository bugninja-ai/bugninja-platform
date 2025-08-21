"""
Cost Repository

This module provides static methods for CRUD operations on Cost entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional

from cuid2 import Cuid as CUID
from sqlmodel import Session, delete, select

from app.db.cost import Cost
from app.schemas.crud.cost import CreateCost, UpdateCost


class CostRepo:
    """
    Repository class for Cost entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, cost_data: CreateCost) -> Cost:
        """
        Create a new cost record in the database.

        Args:
            db: Database session
            cost_data: Cost creation data

        Returns:
            Cost: The created cost instance
        """
        cost = Cost(
            id=CUID().generate(),
            test_run_id=cost_data.test_run_id,
            project_id=cost_data.project_id,
            model_type=cost_data.model_type,
            cost_per_token=cost_data.cost_per_token,
            input_token_num=cost_data.input_token_num,
            completion_token_num=cost_data.completion_token_num,
            cost_in_dollars=cost_data.cost_in_dollars,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(cost)
        db.commit()
        db.refresh(cost)
        return cost

    @staticmethod
    def get_by_id(db: Session, cost_id: str) -> Optional[Cost]:
        """
        Retrieve a cost record by its ID.

        Args:
            db: Database session
            cost_id: Unique cost identifier

        Returns:
            Optional[Cost]: The cost record if found, None otherwise
        """
        statement = select(Cost).where(Cost.id == cost_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_all(db: Session) -> bool:
        db.exec(delete(Cost))  # type: ignore
        db.commit()
        return True

    @staticmethod
    def update(db: Session, cost_id: str, cost_data: UpdateCost) -> Optional[Cost]:
        """
        Update an existing cost record.

        Args:
            db: Database session
            cost_id: Unique cost identifier
            cost_data: Cost update data

        Returns:
            Optional[Cost]: The updated cost record if found, None otherwise
        """
        cost = CostRepo.get_by_id(db, cost_id)
        if not cost:
            return None

        for k, v in cost_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(cost, k, v)

        cost.updated_at = datetime.now(timezone.utc)

        db.add(cost)
        db.commit()
        db.refresh(cost)
        return cost

    @staticmethod
    def delete(db: Session, cost_id: str) -> bool:
        """
        Delete a cost record by its ID.

        Args:
            db: Database session
            cost_id: Unique cost identifier

        Returns:
            bool: True if cost record was deleted, False if not found
        """
        cost = CostRepo.get_by_id(db, cost_id)
        if not cost:
            return False

        db.delete(cost)
        db.commit()
        return True
