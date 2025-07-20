"""
Document Repository

This module provides static methods for CRUD operations on Document entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlmodel import Session, col, select

from app.db.document import Document
from app.schemas.crud.document import CreateDocument, UpdateDocument


class DocumentRepo:
    """
    Repository class for Document entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, document_data: CreateDocument) -> Document:
        """
        Create a new document in the database.

        Args:
            db: Database session
            document_data: Document creation data

        Returns:
            Document: The created document instance
        """
        document = Document(
            id=document_data.id,
            project_id=document_data.project_id,
            name=document_data.name,
            content=document_data.content,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_by_id(db: Session, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            db: Database session
            document_id: Unique document identifier

        Returns:
            Optional[Document]: The document if found, None otherwise
        """
        statement = select(Document).where(Document.id == document_id)
        return db.exec(statement).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Document]:
        """
        Retrieve all documents with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Document]: List of documents
        """
        statement = select(Document).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_project_id(
        db: Session, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Document]:
        """
        Retrieve all documents for a specific project.

        Args:
            db: Database session
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Document]: List of documents for the project
        """
        statement = (
            select(Document).where(Document.project_id == project_id).offset(skip).limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(db: Session, document_id: str, document_data: UpdateDocument) -> Optional[Document]:
        """
        Update an existing document.

        Args:
            db: Database session
            document_id: Unique document identifier
            document_data: Document update data

        Returns:
            Optional[Document]: The updated document if found, None otherwise
        """
        document = DocumentRepo.get_by_id(db, document_id)
        if not document:
            return None

        document.name = document_data.name
        document.content = document_data.content
        document.updated_at = datetime.now(timezone.utc)

        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete(db: Session, document_id: str) -> bool:
        """
        Delete a document by its ID.

        Args:
            db: Database session
            document_id: Unique document identifier

        Returns:
            bool: True if document was deleted, False if not found
        """
        document = DocumentRepo.get_by_id(db, document_id)
        if not document:
            return False

        db.delete(document)
        db.commit()
        return True

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Document]:
        """
        Retrieve a document by its name.

        Args:
            db: Database session
            name: Document name

        Returns:
            Optional[Document]: The document if found, None otherwise
        """
        statement = select(Document).where(Document.name == name)
        return db.exec(statement).first()

    @staticmethod
    def search_by_name(
        db: Session, name_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Document]:
        """
        Search documents by name pattern.

        Args:
            db: Database session
            name_pattern: Name pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Document]: List of matching documents
        """
        statement = (
            select(Document)
            .where(col(Document.name).ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def search_by_content(
        db: Session, content_pattern: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Document]:
        """
        Search documents by content pattern.

        Args:
            db: Database session
            content_pattern: Content pattern to search for (case-insensitive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[Document]: List of matching documents
        """
        statement = (
            select(Document)
            .where(col(Document.content).ilike(f"%{content_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def count_by_project(db: Session, project_id: str) -> int:
        """
        Get the total number of documents for a project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Total number of documents for the project
        """
        statement = select(Document).where(Document.project_id == project_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of documents.

        Args:
            db: Database session

        Returns:
            int: Total number of documents
        """
        statement = select(Document)
        return len(db.exec(statement).all())
