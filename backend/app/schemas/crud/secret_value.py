"""
SecretValue CRUD Schemas

This module defines Pydantic models for SecretValue entity CRUD operations.
Secret values store sensitive configuration data for projects like API keys and passwords.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
    a specific test case and should be encrypted at rest.

    Attributes:
        test_case_id: Reference to the test case this secret belongs to
        secret_name: Human-readable name/identifier for the secret
        secret_value: The actual secret value (should be encrypted)
    """

    test_case_id: str
    secret_name: str
    secret_value: str

    @classmethod
    def sample_factory_build(cls, test_case_id: str = CUID().generate()) -> "CreateSecretValue":
        """
        Generate a sample CreateSecretValue instance for testing.

        Args:
            test_case_id: Test case ID that the secret belongs to

        Returns:
            CreateSecretValue: A sample secret value with fake data
        """

        class CreateSecretValueFactory(ModelFactory[CreateSecretValue]):
            __model__ = CreateSecretValue
            __faker__ = faker

            secret_name = faker.word()
            secret_value = faker.password()

        element = CreateSecretValueFactory.build()
        element.test_case_id = test_case_id

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


class BulkCreateSecretValueRequest(BaseModel):
    """
    Request schema for bulk secret value creation.

    Allows creating multiple secret values in a single request
    with proper validation and error handling.

    Attributes:
        secret_values: List of secret value creation data
    """

    secret_values: List[CreateSecretValue]

    @classmethod
    def sample_factory_build(
        cls, test_case_id: str = CUID().generate()
    ) -> "BulkCreateSecretValueRequest":
        """
        Generate a sample BulkCreateSecretValueRequest instance for testing.

        Args:
            test_case_id: Test case ID that the secrets belong to

        Returns:
            BulkCreateSecretValueRequest: A sample bulk request with fake data
        """
        # Create 3 sample secret values
        secret_values = []
        for i in range(3):
            secret_value = CreateSecretValue.sample_factory_build(test_case_id)
            secret_values.append(secret_value)

        return cls(secret_values=secret_values)


class BulkCreateSecretValueResponse(BaseModel):
    """
    Response schema for bulk secret value creation.

    Contains all created secret values along with detailed information
    about successful and failed operations.

    Attributes:
        created_secret_values: List of newly created secret values
        total_created: Total number of secret values successfully created
        failed_creations: List of failed creation attempts with error details
    """

    created_secret_values: List[ResponseSecretValue]
    total_created: int
    failed_creations: List[Dict[str, Any]]

    @classmethod
    def sample_factory_build(cls, secret_value_count: int = 3) -> "BulkCreateSecretValueResponse":
        """
        Generate a sample BulkCreateSecretValueResponse instance for testing.

        Args:
            secret_value_count: Number of secret values to include

        Returns:
            BulkCreateSecretValueResponse: A sample bulk response with fake data
        """
        # Create sample secret values
        secret_values = []
        for i in range(secret_value_count):
            secret_value = ResponseSecretValue.sample_factory_build()
            secret_values.append(secret_value)

        return cls(
            created_secret_values=secret_values,
            total_created=secret_value_count,
            failed_creations=[],
        )


class UpdateSecretValueWithId(BaseModel):
    """
    Schema for updating an existing secret value with ID.

    Extends UpdateSecretValue with an ID field for bulk operations.

    Attributes:
        id: Unique secret value identifier
        updated_at: Automatically updated timestamp when secret is modified
        secret_name: Updated name/identifier for the secret
        secret_value: Updated secret value (should be encrypted)
    """

    id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    secret_name: Optional[str] = None
    secret_value: Optional[str] = None

    @classmethod
    def sample_factory_build(cls, id: str = CUID().generate()) -> "UpdateSecretValueWithId":
        """
        Generate a sample UpdateSecretValueWithId instance for testing.

        Args:
            id: Secret value ID to use in the sample

        Returns:
            UpdateSecretValueWithId: A sample update secret value with ID and fake data
        """

        class UpdateSecretValueWithIdFactory(ModelFactory[UpdateSecretValueWithId]):
            __model__ = UpdateSecretValueWithId
            __faker__ = faker

            secret_name = faker.word()
            secret_value = faker.password()

        element = UpdateSecretValueWithIdFactory.build()
        element.id = id

        return element


class BulkUpdateSecretValueRequest(BaseModel):
    """
    Request schema for bulk secret value updates.

    Allows updating multiple secret values in a single request.

    Attributes:
        secret_values: List of secret value update data with IDs
    """

    secret_values: List[UpdateSecretValueWithId]

    @classmethod
    def sample_factory_build(cls, secret_value_count: int = 3) -> "BulkUpdateSecretValueRequest":
        """
        Generate a sample BulkUpdateSecretValueRequest instance for testing.

        Args:
            secret_value_count: Number of secret values to include

        Returns:
            BulkUpdateSecretValueRequest: A sample bulk update request with fake data
        """
        # Create sample secret value updates
        secret_values = []
        for i in range(secret_value_count):
            secret_value = UpdateSecretValueWithId.sample_factory_build()
            secret_values.append(secret_value)

        return cls(secret_values=secret_values)


class BulkUpdateSecretValueResponse(BaseModel):
    """
    Response schema for bulk secret value updates.

    Contains all updated secret values along with detailed information
    about successful and failed operations.

    Attributes:
        updated_secret_values: List of successfully updated secret values
        total_updated: Total number of secret values successfully updated
        failed_updates: List of failed update attempts with error details
    """

    updated_secret_values: List[ResponseSecretValue]
    total_updated: int
    failed_updates: List[Dict[str, Any]]

    @classmethod
    def sample_factory_build(cls, secret_value_count: int = 3) -> "BulkUpdateSecretValueResponse":
        """
        Generate a sample BulkUpdateSecretValueResponse instance for testing.

        Args:
            secret_value_count: Number of secret values to include

        Returns:
            BulkUpdateSecretValueResponse: A sample bulk update response with fake data
        """
        # Create sample secret values
        secret_values = []
        for i in range(secret_value_count):
            secret_value = ResponseSecretValue.sample_factory_build()
            secret_values.append(secret_value)

        return cls(
            updated_secret_values=secret_values,
            total_updated=secret_value_count,
            failed_updates=[],
        )


if __name__ == "__main__":
    # Demo: Generate and display sample secret values
    rich_print(CreateSecretValue.sample_factory_build())
    rich_print(UpdateSecretValue.sample_factory_build())
    rich_print(ResponseSecretValue.sample_factory_build())
    rich_print(BulkCreateSecretValueRequest.sample_factory_build())
    rich_print(BulkCreateSecretValueResponse.sample_factory_build())
    rich_print(UpdateSecretValueWithId.sample_factory_build())
    rich_print(BulkUpdateSecretValueRequest.sample_factory_build())
    rich_print(BulkUpdateSecretValueResponse.sample_factory_build())
