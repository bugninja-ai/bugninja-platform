"""
SecretValue CRUD Schemas

This module defines Pydantic models for SecretValue entity CRUD operations.
Secret values store sensitive configuration data for projects like API keys and passwords.
"""

from datetime import datetime, timezone
from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateSecretValue(CreationModel):
    """
    Schema for creating a new secret value.

    Secret values store sensitive configuration data for projects such as
    API keys, passwords, and other credentials. Each secret belongs to
    a specific project and should be encrypted at rest.

    Attributes:
        project_id: Reference to the project this secret belongs to
        secret_name: Human-readable name/identifier for the secret
        secret_value: The actual secret value (should be encrypted)
    """

    project_id: str
    secret_name: str
    secret_value: str

    @classmethod
    def sample_factory_build(cls, project_id: str = CUID().generate()) -> "CreateSecretValue":
        """
        Generate a sample CreateSecretValue instance for testing.

        Args:
            project_id: Project ID that the secret belongs to

        Returns:
            CreateSecretValue: A sample secret value with fake data
        """

        class CreateSecretValueFactory(ModelFactory[CreateSecretValue]):
            __model__ = CreateSecretValue
            __faker__ = faker

            secret_name = faker.word()
            secret_value = faker.password()

        element = CreateSecretValueFactory.build()
        element.project_id = project_id

        return element


class UpdateSecretValue(UpdateModel):
    """
    Schema for updating an existing secret value.

    Allows updating the secret name and value, and automatically
    updates the timestamp when modified.

    Attributes:
        updated_at: Automatically updated timestamp when secret is modified
        secret_name: Updated name/identifier for the secret
        secret_value: Updated secret value (should be encrypted)
    """

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    secret_name: Optional[str] = None
    secret_value: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateSecretValue":
        """
        Generate a sample UpdateSecretValue instance for testing.

        Returns:
            UpdateSecretValue: A sample update secret value with fake data
        """

        class UpdateSecretValueFactory(ModelFactory[UpdateSecretValue]):
            __model__ = UpdateSecretValue
            __faker__ = faker

            secret_name = faker.word()
            secret_value = faker.password()

        element = UpdateSecretValueFactory.build()

        return element


class ResponseSecretValue(BaseModel):
    """
    Schema for secret value responses returned by the API.

    Contains all secret value fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning secret value data to clients.
    Note: The actual secret_value should be masked or encrypted in responses.

    Attributes:
        id: Unique secret value identifier
        project_id: Reference to the project this secret belongs to
        created_at: Timestamp when secret was created
        updated_at: Timestamp when secret was last updated
        secret_name: Human-readable name/identifier for the secret
        secret_value: The secret value (should be masked in responses)
    """

    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    secret_name: str
    secret_value: str

    @classmethod
    def sample_factory_build(
        cls, id: str = CUID().generate(), project_id: str = CUID().generate()
    ) -> "ResponseSecretValue":
        """
        Generate a sample ResponseSecretValue instance for testing.

        Args:
            id: Secret value ID to use in the sample
            project_id: Project ID that the secret belongs to

        Returns:
            ResponseSecretValue: A sample response secret value with fake data
        """

        class ResponseSecretValueFactory(ModelFactory[ResponseSecretValue]):
            __model__ = ResponseSecretValue
            __faker__ = faker

            secret_name = faker.word()
            secret_value = faker.password()

        element = ResponseSecretValueFactory.build()
        element.id = id
        element.project_id = project_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample secret values
    rich_print(CreateSecretValue.sample_factory_build())
    rich_print(UpdateSecretValue.sample_factory_build())
    rich_print(ResponseSecretValue.sample_factory_build())
