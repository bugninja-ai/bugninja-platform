"""
Project Repository

This module provides static methods for CRUD operations on Project entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

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
    def delete(db: Session, project_id: str) -> bool:
        """
        Delete a project by its ID.

        Args:
            db: Database session
            project_id: Unique project identifier

        Returns:
            bool: True if project was deleted, False if not found
        """
        project = ProjectRepo.get_by_id(db, project_id)
        if not project:
            return False

        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Project]:
        """
        Retrieve a project by its name.

        Args:
            db: Database session
            name: Project name

        Returns:
            Optional[Project]: The project if found, None otherwise
        """
        statement = select(Project).where(Project.name == name)
        return db.exec(statement).first()

    @staticmethod
    def search_by_name(
        db: Session, name_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Project]:
        """
        Search projects by name pattern.

        Args:
            db: Database session
            name_pattern: Name pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Project]: List of matching projects
        """
        statement = (
            select(Project)
            .where(col(Project.name).ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

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

    @staticmethod
    def get_all_extended(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[ExtendedResponseProject]:
        """
        Retrieve all projects with extended responses including documents and test cases.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[ExtendedResponseProject]: List of extended project responses
        """
        projects = ProjectRepo.get_all(db, skip, limit)
        extended_projects = []

        for project in projects:
            extended_project = ProjectRepo.get_extended_by_id(db, project.id)
            if extended_project:
                extended_projects.append(extended_project)

        return extended_projects
