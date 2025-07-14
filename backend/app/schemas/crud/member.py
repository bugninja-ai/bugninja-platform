"""
Member CRUD Schemas

This module defines Pydantic models for Member entity CRUD operations.
Members represent users who belong to organizations and can access projects.
"""

from datetime import datetime, timezone

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateMember(CreationModel):
    """
    Schema for creating a new member.

    Members represent users who have access to organizations and their projects.
    Each member is associated with a user account and can have different roles
    within the organization.

    Attributes:
        id: Unique identifier generated using CUID
        user_id: Reference to the user account this member represents
        created_at: Timestamp when the member was created (UTC)
    """

    id: str = Field(default=CUID().generate())
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def sample_factory_build(cls, user_id: str = CUID().generate()) -> "CreateMember":
        """
        Generate a sample CreateMember instance for testing.

        Args:
            user_id: User ID to associate with the member

        Returns:
            CreateMember: A sample member with fake data
        """

        class CreateMemberFactory(ModelFactory[CreateMember]):
            __model__ = CreateMember
            __faker__ = faker

        element = CreateMemberFactory.build()
        element.user_id = user_id

        return element


class UpdateMember(UpdateModel):
    """
    Schema for updating an existing member.

    Currently only allows updating the user_id reference.
    Automatically updates the timestamp when modified.

    Attributes:
        user_id: Updated reference to the user account
    """

    user_id: str

    @classmethod
    def sample_factory_build(cls) -> "UpdateMember":
        """
        Generate a sample UpdateMember instance for testing.

        Returns:
            UpdateMember: A sample update member with fake data
        """

        class UpdateMemberFactory(ModelFactory[UpdateMember]):
            __model__ = UpdateMember
            __faker__ = faker

        element = UpdateMemberFactory.build()

        return element


class ResponseMember(BaseModel):
    """
    Schema for member responses returned by the API.

    Contains all member fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning member data to clients.

    Attributes:
        id: Unique member identifier
        user_id: Reference to the user account this member represents
        created_at: Timestamp when member was created
    """

    id: str
    user_id: str
    created_at: datetime

    @classmethod
    def sample_factory_build(
        cls, id: str = CUID().generate(), user_id: str = CUID().generate()
    ) -> "ResponseMember":
        """
        Generate a sample ResponseMember instance for testing.

        Args:
            id: Member ID to use in the sample
            user_id: User ID to associate with the member

        Returns:
            ResponseMember: A sample response member with fake data
        """

        class ResponseMemberFactory(ModelFactory[ResponseMember]):
            __model__ = ResponseMember
            __faker__ = faker

        element = ResponseMemberFactory.build()
        element.id = id
        element.user_id = user_id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample members
    rich_print(CreateMember.sample_factory_build())
    rich_print(UpdateMember.sample_factory_build())
    rich_print(ResponseMember.sample_factory_build())
