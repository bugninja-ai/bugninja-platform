"""
Secret Value Repository

This module provides static methods for CRUD operations on SecretValue entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

from app.db.secret_value import SecretValue
from app.db.secret_value_test_case import SecretValueTestCase
from app.schemas.crud.secret_value import (
    CreateSecretValue,
    UpdateSecretValue,
    UpdateSecretValueWithId,
)


class SecretValueRepo:
    """
    Repository class for SecretValue entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, secret_value_data: CreateSecretValue) -> SecretValue:
        """
        Create a new secret value in the database.

        Args:
            db: Database session
            secret_value_data: Secret value creation data

        Returns:
            SecretValue: The created secret value instance
        """
        # Lazy import to avoid circular dependency
        from app.repo.test_case_repo import TestCaseRepo

        # Get the test case to retrieve the project_id
        test_case = TestCaseRepo.get_by_id(db, secret_value_data.test_case_id)
        if not test_case:
            raise ValueError(f"Test case with id {secret_value_data.test_case_id} not found")

        secret_value = SecretValue(
            id=CUID().generate(),
            project_id=test_case.project_id,
            secret_name=secret_value_data.secret_name,
            secret_value=secret_value_data.secret_value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(secret_value)
        db.commit()
        db.refresh(secret_value)
        return secret_value

    @staticmethod
    def get_by_id(db: Session, secret_value_id: str) -> Optional[SecretValue]:
        """
        Retrieve a secret value by its ID.

        Args:
            db: Database session
            secret_value_id: Unique secret value identifier

        Returns:
            Optional[SecretValue]: The secret value if found, None otherwise
        """
        statement = select(SecretValue).where(SecretValue.id == secret_value_id)
        return db.exec(statement).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[SecretValue]:
        """
        Retrieve all secret values with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[SecretValue]: List of secret values
        """
        statement = select(SecretValue).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_project_id(
        db: Session, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[SecretValue]:
        """
        Retrieve all secret values for a specific project.

        Args:
            db: Database session
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[SecretValue]: List of secret values for the project
        """
        statement = (
            select(SecretValue)
            .where(SecretValue.project_id == project_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(
        db: Session, secret_value_id: str, secret_value_data: UpdateSecretValue
    ) -> Optional[SecretValue]:
        """
        Update an existing secret value.

        Args:
            db: Database session
            secret_value_id: Unique secret value identifier
            secret_value_data: Secret value update data

        Returns:
            Optional[SecretValue]: The updated secret value if found, None otherwise
        """
        secret_value = SecretValueRepo.get_by_id(db, secret_value_id)
        if not secret_value:
            return None

        for k, v in secret_value_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(secret_value, k, v)

        secret_value.updated_at = datetime.now(timezone.utc)

        db.add(secret_value)
        db.commit()
        db.refresh(secret_value)
        return secret_value

    @staticmethod
    def delete(db: Session, secret_value_id: str) -> bool:
        """
        Delete a secret value by its ID.

        Args:
            db: Database session
            secret_value_id: Unique secret value identifier

        Returns:
            bool: True if secret value was deleted, False if not found
        """
        secret_value = SecretValueRepo.get_by_id(db, secret_value_id)
        if not secret_value:
            return False

        db.delete(secret_value)
        db.commit()
        return True

    @staticmethod
    def get_by_name(db: Session, secret_name: str) -> Optional[SecretValue]:
        """
        Retrieve a secret value by its name.

        Args:
            db: Database session
            secret_name: Secret value name

        Returns:
            Optional[SecretValue]: The secret value if found, None otherwise
        """
        statement = select(SecretValue).where(SecretValue.secret_name == secret_name)
        return db.exec(statement).first()

    @staticmethod
    def get_by_name_and_project(
        db: Session, secret_name: str, project_id: str
    ) -> Optional[SecretValue]:
        """
        Retrieve a secret value by its name and project ID.

        Args:
            db: Database session
            secret_name: Secret value name
            project_id: Project identifier

        Returns:
            Optional[SecretValue]: The secret value if found, None otherwise
        """
        statement = select(SecretValue).where(
            SecretValue.secret_name == secret_name, SecretValue.project_id == project_id
        )
        return db.exec(statement).first()

    @staticmethod
    def search_by_name(
        db: Session, name_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[SecretValue]:
        """
        Search secret values by name pattern.

        Args:
            db: Database session
            name_pattern: Name pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[SecretValue]: List of matching secret values
        """
        statement = (
            select(SecretValue)
            .where(col(SecretValue.secret_name).ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def search_by_name_in_project(
        db: Session, name_pattern: str, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[SecretValue]:
        """
        Search secret values by name pattern within a specific project.

        Args:
            db: Database session
            name_pattern: Name pattern to search for (case-insensitive)
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[SecretValue]: List of matching secret values in the project
        """
        statement = (
            select(SecretValue)
            .where(
                col(SecretValue.secret_name).ilike(f"%{name_pattern}%"),
                SecretValue.project_id == project_id,
            )
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def count_by_project(db: Session, project_id: str) -> int:
        """
        Get the total number of secret values for a project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Total number of secret values for the project
        """
        statement = select(SecretValue).where(SecretValue.project_id == project_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of secret values.

        Args:
            db: Database session

        Returns:
            int: Total number of secret values
        """
        statement = select(SecretValue)
        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_project(db: Session, project_id: str) -> int:
        """
        Delete all secret values for a specific project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Number of secret values deleted
        """
        statement = select(SecretValue).where(SecretValue.project_id == project_id)
        secret_values = db.exec(statement).all()
        count = len(secret_values)

        for secret_value in secret_values:
            db.delete(secret_value)

        db.commit()
        return count

    @staticmethod
    def get_by_test_case_id(db: Session, test_case_id: str) -> Sequence[SecretValue]:
        """
        Retrieve all secret values associated with a specific test case.

        Args:
            db: Database session
            test_case_id: Test case identifier

        Returns:
            Sequence[SecretValue]: List of secret values associated with the test case
        """
        statement = (
            select(SecretValue)
            .join(SecretValueTestCase)
            .where(
                SecretValue.id == SecretValueTestCase.secret_value_id,
                SecretValueTestCase.test_case_id == test_case_id,
            )
        )
        return db.exec(statement).all()

    @staticmethod
    def associate_with_test_case(db: Session, secret_value_id: str, test_case_id: str) -> bool:
        """
        Associate a secret value with a test case.

        Args:
            db: Database session
            secret_value_id: Secret value identifier
            test_case_id: Test case identifier

        Returns:
            bool: True if association was created, False if it already exists
        """
        # Check if association already exists
        existing_association = db.exec(
            select(SecretValueTestCase).where(
                SecretValueTestCase.secret_value_id == secret_value_id,
                SecretValueTestCase.test_case_id == test_case_id,
            )
        ).first()

        if existing_association:
            return False

        # Create new association
        association = SecretValueTestCase(
            secret_value_id=secret_value_id,
            test_case_id=test_case_id,
        )
        db.add(association)
        db.commit()
        return True

    @staticmethod
    def disassociate_from_test_case(db: Session, secret_value_id: str, test_case_id: str) -> bool:
        """
        Remove association between a secret value and a test case.

        Args:
            db: Database session
            secret_value_id: Secret value identifier
            test_case_id: Test case identifier

        Returns:
            bool: True if association was removed, False if it didn't exist
        """
        association = db.exec(
            select(SecretValueTestCase).where(
                SecretValueTestCase.secret_value_id == secret_value_id,
                SecretValueTestCase.test_case_id == test_case_id,
            )
        ).first()

        if not association:
            return False

        db.delete(association)
        db.commit()
        return True

    @staticmethod
    def bulk_create(
        db: Session, secret_values_data: List[CreateSecretValue]
    ) -> Tuple[List[SecretValue], List[Dict[str, Any]]]:
        """
        Create multiple secret values.

        Args:
            db: Database session
            secret_values_data: List of secret value creation data

        Returns:
            Tuple containing:
            - List of created secret values
            - List of failed creations with error details
        """
        created_secret_values = []
        failed_creations = []

        # Lazy import to avoid circular dependency
        from app.repo.test_case_repo import TestCaseRepo

        # Process each secret value
        for index, secret_value_data in enumerate(secret_values_data):
            try:
                # Get the test case to retrieve the project_id
                test_case = TestCaseRepo.get_by_id(db, secret_value_data.test_case_id)
                if not test_case:
                    failed_creations.append(
                        {
                            "index": index,
                            "error": f"Test case with id {secret_value_data.test_case_id} not found",
                            "data": secret_value_data.model_dump(),
                        }
                    )
                    continue

                # Check for duplicate secret names in the same project
                existing_secret = SecretValueRepo.get_by_name_and_project(
                    db, secret_value_data.secret_name, test_case.project_id
                )
                if existing_secret:
                    failed_creations.append(
                        {
                            "index": index,
                            "error": f"Secret with name '{secret_value_data.secret_name}' already exists in project",
                            "data": secret_value_data.model_dump(),
                        }
                    )
                    continue

                # Create secret value
                secret_value = SecretValue(
                    id=CUID().generate(),
                    project_id=test_case.project_id,
                    secret_name=secret_value_data.secret_name,
                    secret_value=secret_value_data.secret_value,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(secret_value)
                created_secret_values.append(secret_value)

            except Exception as e:
                failed_creations.append(
                    {
                        "index": index,
                        "error": str(e),
                        "data": secret_value_data.model_dump(),
                    }
                )

        # Commit all successful creations
        if created_secret_values:
            db.commit()

        return created_secret_values, failed_creations

    @staticmethod
    def bulk_update(
        db: Session, secret_values_data: List[UpdateSecretValueWithId]
    ) -> Tuple[List[SecretValue], List[Dict[str, Any]]]:
        """
        Update multiple secret values.

        Args:
            db: Database session
            secret_values_data: List of secret value update data with IDs

        Returns:
            Tuple containing:
            - List of updated secret values
            - List of failed updates with error details
        """
        updated_secret_values = []
        failed_updates = []

        # Process each secret value update
        for index, secret_value_data in enumerate(secret_values_data):
            try:
                # Check if secret value exists
                existing_secret_value = SecretValueRepo.get_by_id(db, secret_value_data.id)
                if not existing_secret_value:
                    failed_updates.append(
                        {
                            "index": index,
                            "error": f"Secret value with id {secret_value_data.id} not found",
                            "data": secret_value_data.model_dump(),
                        }
                    )
                    continue

                # Check for duplicate secret names if secret_name is being updated
                if (
                    secret_value_data.secret_name
                    and secret_value_data.secret_name != existing_secret_value.secret_name
                ):
                    existing_secret = SecretValueRepo.get_by_name_and_project(
                        db, secret_value_data.secret_name, existing_secret_value.project_id
                    )
                    if existing_secret and existing_secret.id != secret_value_data.id:
                        failed_updates.append(
                            {
                                "index": index,
                                "error": f"Secret with name '{secret_value_data.secret_name}' already exists in project",
                                "data": secret_value_data.model_dump(),
                            }
                        )
                        continue

                # Update secret value fields
                update_data = secret_value_data.model_dump(
                    exclude_unset=True, exclude_none=True, exclude={"id"}
                )

                for field, value in update_data.items():
                    setattr(existing_secret_value, field, value)

                # Update timestamp
                existing_secret_value.updated_at = datetime.now(timezone.utc)

                db.add(existing_secret_value)
                updated_secret_values.append(existing_secret_value)

            except Exception as e:
                failed_updates.append(
                    {
                        "index": index,
                        "error": str(e),
                        "data": secret_value_data.model_dump(),
                    }
                )

        # Commit all successful updates
        if updated_secret_values:
            db.commit()

        return updated_secret_values, failed_updates
