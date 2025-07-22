"""
Cost Repository

This module provides static methods for CRUD operations on Cost entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlmodel import Session, col, select

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
            id=cost_data.id,
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
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Cost]:
        """
        Retrieve all cost records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Cost]: List of cost records
        """
        statement = select(Cost).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_test_run_id(db: Session, test_run_id: str) -> Optional[Cost]:
        """
        Retrieve a cost record by its associated test run ID.

        Args:
            db: Database session
            test_run_id: Test run identifier

        Returns:
            Optional[Cost]: The cost record if found, None otherwise
        """
        statement = select(Cost).where(Cost.test_run_id == test_run_id)
        return db.exec(statement).first()

    @staticmethod
    def get_by_project_id(
        db: Session, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Cost]:
        """
        Retrieve all cost records for a specific project.

        Args:
            db: Database session
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Cost]: List of cost records for the project
        """
        statement = select(Cost).where(Cost.project_id == project_id).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_model_type(
        db: Session, model_type: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Cost]:
        """
        Retrieve all cost records for a specific model type.

        Args:
            db: Database session
            model_type: Model type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Cost]: List of cost records for the model type
        """
        statement = select(Cost).where(Cost.model_type == model_type).offset(skip).limit(limit)
        return db.exec(statement).all()

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

    @staticmethod
    def get_total_cost_by_project(db: Session, project_id: str) -> float:
        """
        Get the total cost in dollars for a specific project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            float: Total cost in dollars for the project
        """
        statement = select(Cost).where(Cost.project_id == project_id)
        costs = db.exec(statement).all()
        return sum(cost.cost_in_dollars for cost in costs)

    @staticmethod
    def get_total_cost_by_model_type(db: Session, model_type: str) -> float:
        """
        Get the total cost in dollars for a specific model type.

        Args:
            db: Database session
            model_type: Model type to filter by

        Returns:
            float: Total cost in dollars for the model type
        """
        statement = select(Cost).where(Cost.model_type == model_type)
        costs = db.exec(statement).all()
        return sum(cost.cost_in_dollars for cost in costs)

    @staticmethod
    def get_total_tokens_by_project(db: Session, project_id: str) -> tuple[int, int]:
        """
        Get the total input and completion tokens for a specific project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            tuple[int, int]: Total input tokens and completion tokens
        """
        statement = select(Cost).where(Cost.project_id == project_id)
        costs = db.exec(statement).all()
        total_input = sum(cost.input_token_num for cost in costs)
        total_completion = sum(cost.completion_token_num for cost in costs)
        return total_input, total_completion

    @staticmethod
    def get_total_tokens_by_model_type(db: Session, model_type: str) -> tuple[int, int]:
        """
        Get the total input and completion tokens for a specific model type.

        Args:
            db: Database session
            model_type: Model type to filter by

        Returns:
            tuple[int, int]: Total input tokens and completion tokens
        """
        statement = select(Cost).where(Cost.model_type == model_type)
        costs = db.exec(statement).all()
        total_input = sum(cost.input_token_num for cost in costs)
        total_completion = sum(cost.completion_token_num for cost in costs)
        return total_input, total_completion

    @staticmethod
    def count_by_project(db: Session, project_id: str) -> int:
        """
        Get the total number of cost records for a project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Total number of cost records for the project
        """
        statement = select(Cost).where(Cost.project_id == project_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count_by_model_type(db: Session, model_type: str) -> int:
        """
        Get the total number of cost records for a model type.

        Args:
            db: Database session
            model_type: Model type to filter by

        Returns:
            int: Total number of cost records for the model type
        """
        statement = select(Cost).where(Cost.model_type == model_type)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of cost records.

        Args:
            db: Database session

        Returns:
            int: Total number of cost records
        """
        statement = select(Cost)
        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_project(db: Session, project_id: str) -> int:
        """
        Delete all cost records for a specific project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Number of cost records deleted
        """
        statement = select(Cost).where(Cost.project_id == project_id)
        costs = db.exec(statement).all()
        count = len(costs)

        for cost in costs:
            db.delete(cost)

        db.commit()
        return count

    @staticmethod
    def delete_by_test_run(db: Session, test_run_id: str) -> int:
        """
        Delete all cost records for a specific test run.

        Args:
            db: Database session
            test_run_id: Test run identifier

        Returns:
            int: Number of cost records deleted
        """
        statement = select(Cost).where(Cost.test_run_id == test_run_id)
        costs = db.exec(statement).all()
        count = len(costs)

        for cost in costs:
            db.delete(cost)

        db.commit()
        return count

    @staticmethod
    def get_most_expensive_runs(db: Session, limit: int = 10) -> Sequence[Cost]:
        """
        Get the most expensive test runs.

        Args:
            db: Database session
            limit: Maximum number of records to return

        Returns:
            Sequence[Cost]: List of most expensive cost records
        """
        statement = select(Cost).order_by(col(Cost.cost_in_dollars).desc()).limit(limit)
        return db.exec(statement).all()
