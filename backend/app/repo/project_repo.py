"""
Project Repository

This module provides static methods for CRUD operations on Project entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlalchemy import UnaryExpression
from sqlmodel import Session, col, delete, select

from app.db.document import Document
from app.db.project import Project
from app.db.test_case import TestCase
from app.schemas.communication.project import (
    ExtendedResponseProject,
    LightResponseTestcase,
    ResponseSecretsOfProject,
)
from app.schemas.crud.document import ResponseDocument
from app.schemas.crud.project import CreateProject, UpdateProject
from app.schemas.crud.secret_value import ResponseSecretValue


class ProjectRepo:
    """
    Repository class for Project entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, project_data: CreateProject) -> Project:
        """
        Create a new project in the database.

        Args:
            db: Database session
            project_data: Project creation data

        Returns:
            Project: The created project instance
        """
        project = Project(
            id=CUID().generate(),
            name=project_data.name,
            default_start_url=project_data.default_start_url,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_by_id(db: Session, project_id: str) -> Optional[Project]:
        """
        Retrieve a project by its ID.

        Args:
            db: Database session
            project_id: Unique project identifier

        Returns:
            Optional[Project]: The project if found, None otherwise
        """
        statement = select(Project).where(Project.id == project_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_all(db: Session) -> bool:
        db.exec(delete(Project))  # type: ignore
        db.commit()
        return True

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Project]:
        """
        Retrieve all projects with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Project]: List of projects
        """
        statement = select(Project).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_all_with_sorting(
        db: Session, page: int = 1, page_size: int = 10, sort_order: str = "desc"
    ) -> Sequence[Project]:
        """
        Retrieve all projects with pagination and sorting by creation date.

        Args:
            db: Database session
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)
            sort_order: Sort order - "asc" for ascending, "desc" for descending (default: "desc")

        Returns:
            Sequence[Project]: List of projects sorted by creation date
        """
        # Calculate skip based on page and page_size
        skip = (page - 1) * page_size

        order_by: UnaryExpression[datetime]
        if sort_order.lower() == "asc":
            order_by = col(Project.created_at).asc()

        else:
            order_by = col(Project.created_at).desc()

        return db.exec(
            statement=(select(Project).order_by(order_by).offset(skip).limit(page_size))
        ).all()

    @staticmethod
    def update(db: Session, project_id: str, project_data: UpdateProject) -> Optional[Project]:
        """
        Update an existing project.

        Args:
            db: Database session
            project_id: Unique project identifier
            project_data: Project update data

        Returns:
            Optional[Project]: The updated project if found, None otherwise
        """
        project = ProjectRepo.get_by_id(db, project_id)
        if not project:
            return None

        for k, v in project_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(project, k, v)

        project.updated_at = datetime.now(timezone.utc)

        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of projects.

        Args:
            db: Database session

        Returns:
            int: Total number of projects
        """
        statement = select(Project)
        return len(db.exec(statement).all())

    @staticmethod
    def delete(db: Session, project_id: str) -> bool:
        """
        Delete a project by its ID with comprehensive cascade deletion.

        This method performs cascade deletion in the following order to respect foreign key constraints:
        1. Delete all actions associated with brain states (through test traversals)
        2. Delete all brain states associated with test traversals
        3. Delete all history elements and costs associated with test runs
        4. Delete all test runs associated with test traversals
        5. Delete all test traversals associated with test cases
        6. Delete all browser config associations (TestCaseBrowserConfig)
        7. Delete all secret value associations (SecretValueTestCase)
        8. Delete all test cases
        9. Delete all browser configurations
        10. Delete all secret values
        11. Delete all documents
        12. Delete all costs directly associated with project
        13. Delete the project itself

        This ensures that all related data is properly cleaned up before attempting
        to delete the project, preventing foreign key constraint violations.

        Args:
            db: Database session
            project_id: Unique project identifier

        Returns:
            bool: True if project was deleted, False if not found

        Raises:
            Exception: If any database operation fails, transaction is rolled back
        """
        project = ProjectRepo.get_by_id(db, project_id)
        if not project:
            return False

        try:
            # Import here to avoid circular imports
            from app.db.action import Action
            from app.db.brain_state import BrainState
            from app.db.browser_config import BrowserConfig
            from app.db.cost import Cost
            from app.db.document import Document
            from app.db.history_element import HistoryElement
            from app.db.secret_value import SecretValue
            from app.db.secret_value_test_case import SecretValueTestCase
            from app.db.test_case import TestCase
            from app.db.test_case_browser_config import TestCaseBrowserConfig
            from app.db.test_run import TestRun
            from app.db.test_traversal import TestTraversal

            # 1. Get all test cases for this project
            test_cases = db.exec(select(TestCase).where(TestCase.project_id == project_id)).all()

            # 2. Delete cascade starting from the deepest level: Actions -> BrainStates -> TestRuns -> TestTraversals -> TestCases
            for test_case in test_cases:
                # Get all test traversals for this test case
                traversals = db.exec(
                    select(TestTraversal).where(TestTraversal.test_case_id == test_case.id)
                ).all()

                for traversal in traversals:
                    # Delete all actions through brain states
                    brain_states = db.exec(
                        select(BrainState).where(BrainState.test_traversal_id == traversal.id)
                    ).all()

                    for brain_state in brain_states:
                        # Delete all actions for this brain state
                        actions = db.exec(
                            select(Action).where(Action.brain_state_id == brain_state.id)
                        ).all()
                        for action in actions:
                            db.delete(action)

                    # Delete all brain states for this traversal
                    for brain_state in brain_states:
                        db.delete(brain_state)

                    # Delete all test runs for this traversal
                    test_runs = db.exec(
                        select(TestRun).where(TestRun.test_traversal_id == traversal.id)
                    ).all()

                    for test_run in test_runs:
                        # Delete history elements for this test run
                        history_elements = db.exec(
                            select(HistoryElement).where(HistoryElement.test_run_id == test_run.id)
                        ).all()
                        for history_element in history_elements:
                            db.delete(history_element)

                        # Delete cost associated with this test run
                        costs = db.exec(select(Cost).where(Cost.test_run_id == test_run.id)).all()
                        for cost in costs:
                            db.delete(cost)

                        # Delete the test run itself
                        db.delete(test_run)

                # Delete all test traversals for this test case
                for traversal in traversals:
                    db.delete(traversal)

                # Delete browser config associations for this test case
                browser_config_associations = db.exec(
                    select(TestCaseBrowserConfig).where(
                        TestCaseBrowserConfig.test_case_id == test_case.id
                    )
                ).all()
                for browser_association in browser_config_associations:
                    db.delete(browser_association)

                # Delete secret value associations for this test case
                secret_associations = db.exec(
                    select(SecretValueTestCase).where(
                        SecretValueTestCase.test_case_id == test_case.id
                    )
                ).all()
                for secret_association in secret_associations:
                    db.delete(secret_association)

                # Delete the test case itself
                db.delete(test_case)

            # 3. Delete all browser configurations for this project
            browser_configs = db.exec(
                select(BrowserConfig).where(BrowserConfig.project_id == project_id)
            ).all()
            for browser_config in browser_configs:
                db.delete(browser_config)

            # 4. Delete all secret values for this project
            secret_values = db.exec(
                select(SecretValue).where(SecretValue.project_id == project_id)
            ).all()
            for secret_value in secret_values:
                db.delete(secret_value)

            # 5. Delete all documents for this project
            documents = db.exec(select(Document).where(Document.project_id == project_id)).all()
            for document in documents:
                db.delete(document)

            # 6. Delete all remaining costs directly associated with this project
            remaining_costs = db.exec(select(Cost).where(Cost.project_id == project_id)).all()
            for cost in remaining_costs:
                db.delete(cost)

            # 7. Finally, delete the project itself
            db.delete(project)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise e

    # Extended Response Methods

    @staticmethod
    def get_extended_by_id(db: Session, project_id: str) -> Optional[ExtendedResponseProject]:
        """
        Retrieve an extended project response with nested documents and test cases.

        Args:
            db: Database session
            project_id: Unique project identifier

        Returns:
            Optional[ExtendedResponseProject]: The extended project response if found, None otherwise
        """
        # Get the project
        project = ProjectRepo.get_by_id(db, project_id)
        if not project:
            return None

        # Get associated documents
        documents_statement = select(Document).where(Document.project_id == project_id)
        documents = db.exec(documents_statement).all()

        # Get associated test cases
        test_cases_statement = select(TestCase).where(TestCase.project_id == project_id)
        test_cases = db.exec(test_cases_statement).all()

        # Convert documents to ResponseDocument
        response_documents = [
            ResponseDocument(
                id=doc.id,
                project_id=doc.project_id,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                name=doc.name,
                content=doc.content,
            )
            for doc in documents
        ]

        # Convert test cases to LightResponseTestcase
        light_test_cases = [
            LightResponseTestcase(
                id=tc.id,
                document_id=tc.document_id,
                name=tc.test_name,  # Using test_name as the name
                created_at=tc.created_at,
                updated_at=tc.updated_at,
                test_name=tc.test_name,
            )
            for tc in test_cases
        ]

        return ExtendedResponseProject(
            id=project.id,
            organization_id="",  # TODO: Add organization_id to Project model if needed
            name=project.name,
            created_at=project.created_at,
            default_start_url=project.default_start_url,
            documents=response_documents,
            test_cases=light_test_cases,
        )

    @staticmethod
    def get_secrets_of_project(db: Session, project_id: str) -> Optional[ResponseSecretsOfProject]:
        """
        Retrieve all secrets for a specific project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            Optional[ResponseSecretsOfProject]: The project secrets response if found, None otherwise
        """
        # Verify project exists
        project = ProjectRepo.get_by_id(db, project_id)
        if not project:
            return None

        # Import here to avoid circular imports
        from app.repo.secret_value_repo import SecretValueRepo

        # Get secret values for the project
        secret_values = SecretValueRepo.get_by_project_id(db, project_id)

        # Convert to ResponseSecretValue
        response_secrets = [
            ResponseSecretValue(
                id=sv.id,
                project_id=sv.project_id,
                secret_name=sv.secret_name,
                secret_value=sv.secret_value,
                created_at=sv.created_at,
                updated_at=sv.updated_at,
            )
            for sv in secret_values
        ]

        return ResponseSecretsOfProject(
            project_id=project_id,
            secret_list=response_secrets,
        )
