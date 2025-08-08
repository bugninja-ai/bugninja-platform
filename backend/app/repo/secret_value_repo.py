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
        db: Session,
        secret_values_data: Optional[List[UpdateSecretValueWithId]] = None,
        new_secret_values: Optional[List[CreateSecretValue]] = None,
        existing_secret_value_ids_to_add: Optional[List[str]] = None,
        secret_value_ids_to_unlink: Optional[List[str]] = None,
        test_case_id: Optional[str] = None,
    ) -> Tuple[
        List[SecretValue],
        List[SecretValue],
        List[SecretValue],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        int,
    ]:
        """
        Update multiple secret values, create new ones, link existing ones, and unlink secrets.

        Args:
            db: Database session
            secret_values_data: List of secret value update data with IDs
            new_secret_values: List of new secret values to create and link
            existing_secret_value_ids_to_add: List of existing secret IDs to link to test case
            secret_value_ids_to_unlink: List of secret IDs to unlink from test case
            test_case_id: Test case ID for linking/unlinking operations

        Returns:
            Tuple containing:
            - List of updated secret values
            - List of created secret values
            - List of linked secret values
            - List of failed updates with error details
            - List of failed creations with error details
            - List of failed links with error details
            - Number of unlinked secrets
        """
        updated_secret_values: List[SecretValue] = []
        created_secret_values: List[SecretValue] = []
        linked_secret_values: List[SecretValue] = []
        failed_updates: List[Dict[str, Any]] = []
        failed_creations: List[Dict[str, Any]] = []
        failed_links: List[Dict[str, Any]] = []
        unlinked_count = 0

        # Handle secret value updates
        if secret_values_data:
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

        # Handle creating new secret values
        if new_secret_values and test_case_id:
            created_secret_values, failed_creations = SecretValueRepo.bulk_create(
                db, new_secret_values
            )

            # Link new secret values to test case
            if created_secret_values:
                SecretValueRepo._associate_secret_values_with_test_case(
                    db, test_case_id, [sv.id for sv in created_secret_values]
                )

        # Handle linking existing secret values
        if existing_secret_value_ids_to_add and test_case_id:
            for secret_id in existing_secret_value_ids_to_add:
                try:
                    secret_value = SecretValueRepo.get_by_id(db, secret_id)
                    if secret_value:
                        # Check if not already linked
                        existing_link = db.exec(
                            select(SecretValueTestCase)
                            .where(SecretValueTestCase.secret_value_id == secret_id)
                            .where(SecretValueTestCase.test_case_id == test_case_id)
                        ).first()

                        if not existing_link:
                            SecretValueRepo._associate_secret_values_with_test_case(
                                db, test_case_id, [secret_id]
                            )
                            linked_secret_values.append(secret_value)
                    else:
                        failed_links.append(
                            {
                                "secret_id": secret_id,
                                "error": f"Secret value with id {secret_id} not found",
                            }
                        )
                except Exception as e:
                    failed_links.append({"secret_id": secret_id, "error": str(e)})

        # Handle unlinking secret values
        if secret_value_ids_to_unlink and test_case_id:
            for secret_id in secret_value_ids_to_unlink:
                try:
                    # Remove the association
                    association = db.exec(
                        select(SecretValueTestCase)
                        .where(SecretValueTestCase.secret_value_id == secret_id)
                        .where(SecretValueTestCase.test_case_id == test_case_id)
                    ).first()

                    if association:
                        db.delete(association)
                        unlinked_count += 1
                except Exception:
                    # Log error but don't fail the operation
                    pass

        # Commit all changes
        db.commit()

        return (
            updated_secret_values,
            created_secret_values,
            linked_secret_values,
            failed_updates,
            failed_creations,
            failed_links,
            unlinked_count,
        )

    @staticmethod
    def _associate_secret_values_with_test_case(
        db: Session, test_case_id: str, secret_value_ids: List[str]
    ) -> None:
        """
        Associate secret values with a test case.

        Args:
            db: Database session
            test_case_id: Test case ID
            secret_value_ids: List of secret value IDs to associate
        """
        for secret_value_id in secret_value_ids:
            # Check if association already exists
            existing_association = db.exec(
                select(SecretValueTestCase)
                .where(SecretValueTestCase.secret_value_id == secret_value_id)
                .where(SecretValueTestCase.test_case_id == test_case_id)
            ).first()

            if not existing_association:
                association = SecretValueTestCase(
                    secret_value_id=secret_value_id,
                    test_case_id=test_case_id,
                )
                db.add(association)

    @staticmethod
    def check_usage(db: Session, secret_value_id: str) -> Tuple[bool, str]:
        """
        Check if a secret value is still being used by test cases.

        Args:
            db: Database session
            secret_value_id: Secret value identifier

        Returns:
            Tuple[bool, str]: (is_in_use, usage_details)
        """
        # Check test case associations
        test_case_associations = db.exec(
            select(SecretValueTestCase).where(
                SecretValueTestCase.secret_value_id == secret_value_id
            )
        ).all()

        if test_case_associations:
            return True, f"{len(test_case_associations)} test case(s)"
        else:
            return False, ""
