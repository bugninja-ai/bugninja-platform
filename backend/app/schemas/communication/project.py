"""
Project Communication Schemas

This module defines Pydantic models for project-related communication responses.
These schemas are used for API responses that include nested project data and related entities.
"""

from datetime import datetime
from typing import List, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.schemas.crud.base import faker
from app.schemas.crud.document import ResponseDocument
from app.schemas.crud.secret_value import ResponseSecretValue


class LightResponseTestcase(BaseModel):
    """
    Lightweight test case response for project communication.

    Contains essential test case information without full details,
    used when listing test cases within project responses.

    Attributes:
        id: Unique test case identifier
        document_id: Optional reference to associated document
        name: Human-readable name for the test case
        created_at: Timestamp when test case was created
        updated_at: Timestamp when test case was last updated
        test_name: Specific test name/identifier
    """

    id: str
    document_id: Optional[str]
    name: str
    created_at: datetime
    updated_at: datetime
    test_name: str

    @classmethod
    def sample_factory_build(
        cls, id: str = CUID().generate(), document_id: Optional[str] = CUID().generate()
    ) -> "LightResponseTestcase":
        """
        Generate a sample LightResponseTestcase instance for testing.

        Args:
            id: Test case ID to use in the sample
            document_id: Optional document ID to associate with the test case

        Returns:
            LightResponseTestcase: A sample lightweight test case with fake data
        """

        class LightResponseTestcaseFactory(ModelFactory[LightResponseTestcase]):
            __model__ = LightResponseTestcase
            __faker__ = faker

            name = faker.catch_phrase()
            test_name = faker.catch_phrase()

        element = LightResponseTestcaseFactory.build()
        element.id = id
        element.document_id = document_id

        return element


class ResponseSecretsOfProject(BaseModel):
    """
    Response schema for project secrets listing.

    Contains project identification and a list of associated secret values.
    Used when returning all secrets for a specific project.

    Attributes:
        project_id: Reference to the project these secrets belong to
        secret_list: List of secret values associated with the project
    """

    project_id: str
    secret_list: List[ResponseSecretValue]

    @classmethod
    def sample_factory_build(
        cls, project_id: str = CUID().generate(), secret_count: int = 3
    ) -> "ResponseSecretsOfProject":
        """
        Generate a sample ResponseSecretsOfProject instance for testing.

        Args:
            project_id: Project ID to use in the sample
            secret_count: Number of secret values to generate

        Returns:
            ResponseSecretsOfProject: A sample project secrets response with fake data
        """

        secret_list = [
            ResponseSecretValue.sample_factory_build(project_id=project_id)
            for _ in range(secret_count)
        ]

        return ResponseSecretsOfProject(project_id=project_id, secret_list=secret_list)


class ExtendedResponseProject(BaseModel):
    """
    Extended project response with nested related entities.

    Contains full project information along with associated documents
    and test cases. Used for comprehensive project data retrieval.

    Attributes:
        id: Unique project identifier
        organization_id: Reference to the organization this project belongs to
        name: Human-readable name for the project
        created_at: Timestamp when project was created
        default_start_url: Default URL where tests for this project start
        documents: List of documents associated with this project
        test_cases: List of lightweight test case information
    """

    id: str
    organization_id: str
    name: str
    created_at: datetime
    default_start_url: str
    documents: List[ResponseDocument]
    test_cases: List[LightResponseTestcase]

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        organization_id: str = CUID().generate(),
        document_count: int = 2,
        test_case_count: int = 3,
    ) -> "ExtendedResponseProject":
        """
        Generate a sample ExtendedResponseProject instance for testing.

        Args:
            id: Project ID to use in the sample
            organization_id: Organization ID to use in the sample
            document_count: Number of documents to generate
            test_case_count: Number of test cases to generate

        Returns:
            ExtendedResponseProject: A sample extended project response with fake data
        """

        class ExtendedResponseProjectFactory(ModelFactory[ExtendedResponseProject]):
            __model__ = ExtendedResponseProject
            __faker__ = faker

            name = faker.catch_phrase()
            default_start_url = faker.url()

        element = ExtendedResponseProjectFactory.build()
        element.id = id
        element.organization_id = organization_id

        # Generate sample documents
        documents = [
            ResponseDocument.sample_factory_build(project_id=id) for _ in range(document_count)
        ]

        # Generate sample test cases
        test_cases = [
            LightResponseTestcase.sample_factory_build(
                document_id=documents[i % len(documents)].id if documents else None
            )
            for i in range(test_case_count)
        ]

        element.documents = documents
        element.test_cases = test_cases

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample communication schemas
    rich_print("=== LightResponseTestcase Sample ===")
    rich_print(LightResponseTestcase.sample_factory_build())

    rich_print("\n=== ResponseSecretsOfProject Sample ===")
    rich_print(ResponseSecretsOfProject.sample_factory_build())

    rich_print("\n=== ExtendedResponseProject Sample ===")
    rich_print(ExtendedResponseProject.sample_factory_build())
