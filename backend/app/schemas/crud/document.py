"""
Document CRUD Schemas

This module defines Pydantic models for Document entity CRUD operations.
Documents represent content that can be associated with test cases and projects.
"""

from datetime import datetime, timezone
from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateDocument(CreationModel):
    """
    Schema for creating a new document.

    Documents can be standalone or associated with a specific test case.
    Each document belongs to a project and contains name and content fields.

    Attributes:
        project_id: Required reference to the project this document belongs to
        name: Human-readable name/title for the document
        content: The actual document content/text
    """

    project_id: str
    name: str
    content: str

    @classmethod
    def sample_factory_build(cls, project_id: str = CUID().generate()) -> "CreateDocument":
        """
        Generate a sample CreateDocument instance for testing.

        Args:
            test_case_id: Optional test case ID to associate with the document
            project_id: Project ID that the document belongs to

        Returns:
            CreateDocument: A sample document with fake data
        """

        class CreateDocumentFactory(ModelFactory[CreateDocument]):
            __model__ = CreateDocument
            __faker__ = faker

            name = faker.name_male()
            content = faker.paragraph(nb_sentences=30)

        element = CreateDocumentFactory.build()
        element.project_id = project_id

        return element


class UpdateDocument(UpdateModel):
    """
    Schema for updating an existing document.

    Only allows updating the name, content, and automatically updates the timestamp.
    The document ID and relationships remain unchanged.

    Attributes:
        updated_at: Automatically updated timestamp when document is modified
        name: Updated name/title for the document
        content: Updated document content/text
    """

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    name: Optional[str] = None
    content: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateDocument":
        """
        Generate a sample UpdateDocument instance for testing.

        Returns:
            UpdateDocument: A sample update document with fake data
        """

        class UpdateDocumentFactory(ModelFactory[UpdateDocument]):
            __model__ = UpdateDocument
            __faker__ = faker

            name = faker.name_male()
            content = faker.paragraph(nb_sentences=30)

        element = UpdateDocumentFactory.build()

        return element


class ResponseDocument(BaseModel):
    """
    Schema for document responses returned by the API.

    Contains all document fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning document data to clients.

    Attributes:
        id: Unique document identifier
        test_case_id: Optional reference to associated test case
        project_id: Reference to the project this document belongs to
        created_at: Timestamp when document was created
        updated_at: Timestamp when document was last updated
        name: Document name/title
        content: Document content/text
    """

    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    name: str
    content: str

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        test_case_id: str = CUID().generate(),
        project_id: str = CUID().generate(),
    ) -> "ResponseDocument":
        """
        Generate a sample ResponseDocument instance for testing.

        Args:
            id: Document ID to use in the sample
            test_case_id: Test case ID to associate with the document
            project_id: Project ID that the document belongs to

        Returns:
            ResponseDocument: A sample response document with fake data
        """

        class ResponseDocumentFactory(ModelFactory[ResponseDocument]):
            __model__ = ResponseDocument
            __faker__ = faker

            name = faker.name_male()
            content = faker.paragraph(nb_sentences=30)

        element = ResponseDocumentFactory.build()
        element.id = id
        element.project_id = project_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample documents
    rich_print(CreateDocument.sample_factory_build())
    rich_print(UpdateDocument.sample_factory_build())
    rich_print(ResponseDocument.sample_factory_build())
