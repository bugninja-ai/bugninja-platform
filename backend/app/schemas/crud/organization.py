"""
Organization CRUD Schemas

This module defines Pydantic models for Organization entity CRUD operations.
Organizations represent companies or teams that can contain multiple projects.
"""

from datetime import datetime, timezone

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateOrganization(CreationModel):
    """
    Schema for creating a new organization.

    Organizations represent companies or teams that can contain multiple projects.
    Each organization can have multiple members and projects associated with it.

    Attributes:
        id: Unique identifier generated using CUID
        name: Human-readable name for the organization
        created_at: Timestamp when the organization was created (UTC)
        logo: URL or path to the organization's logo image
    """

    id: str = Field(default=CUID().generate())
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    logo: str

    @classmethod
    def sample_factory_build(cls) -> "CreateOrganization":
        """
        Generate a sample CreateOrganization instance for testing.

        Returns:
            CreateOrganization: A sample organization with fake data
        """

        class CreateOrganizationFactory(ModelFactory[CreateOrganization]):
            __model__ = CreateOrganization
            __faker__ = faker

            name = faker.company()
            logo = faker.image_url()

        element = CreateOrganizationFactory.build()

        return element


class UpdateOrganization(UpdateModel):
    """
    Schema for updating an existing organization.

    Allows updating the name and logo, and automatically updates the timestamp.

    Attributes:
        name: Updated name for the organization
        logo: Updated URL or path to the organization's logo
    """

    name: str
    logo: str

    @classmethod
    def sample_factory_build(cls) -> "UpdateOrganization":
        """
        Generate a sample UpdateOrganization instance for testing.

        Returns:
            UpdateOrganization: A sample update organization with fake data
        """

        class UpdateOrganizationFactory(ModelFactory[UpdateOrganization]):
            __model__ = UpdateOrganization
            __faker__ = faker

            name = faker.company()
            logo = faker.image_url()

        element = UpdateOrganizationFactory.build()

        return element


class ResponseOrganization(BaseModel):
    """
    Schema for organization responses returned by the API.

    Contains all organization fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning organization data to clients.

    Attributes:
        id: Unique organization identifier
        name: Human-readable name for the organization
        created_at: Timestamp when organization was created
        logo: URL or path to the organization's logo image
    """

    id: str
    name: str
    created_at: datetime
    logo: str

    @classmethod
    def sample_factory_build(cls, id: str = CUID().generate()) -> "ResponseOrganization":
        """
        Generate a sample ResponseOrganization instance for testing.

        Args:
            id: Organization ID to use in the sample

        Returns:
            ResponseOrganization: A sample response organization with fake data
        """

        class ResponseOrganizationFactory(ModelFactory[ResponseOrganization]):
            __model__ = ResponseOrganization
            __faker__ = faker

            name = faker.company()
            logo = faker.image_url()

        element = ResponseOrganizationFactory.build()
        element.id = id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample organizations
    rich_print(CreateOrganization.sample_factory_build())
    rich_print(UpdateOrganization.sample_factory_build())
    rich_print(ResponseOrganization.sample_factory_build())
