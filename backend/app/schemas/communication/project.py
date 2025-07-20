"""
Project Communication Schemas

This module defines Pydantic models for project-related communication responses.
These schemas are used for API responses that include nested project data and related entities.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

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
