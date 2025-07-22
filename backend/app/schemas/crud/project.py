"""
Project CRUD Schemas

This module defines Pydantic models for Project entity CRUD operations.
Projects represent specific testing initiatives.
"""

from datetime import datetime
from typing import Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateProject(CreationModel):
    """
    Schema for creating a new project.

    Projects represent specific testing initiatives.
    Each project can contain multiple test cases, documents, and other testing resources.

    Attributes:
        name: Human-readable name for the project
        default_start_url: Default URL where tests for this project start
    """

    name: str
    default_start_url: str

    @classmethod
    def sample_factory_build(cls) -> "CreateProject":
        """
        Generate a sample CreateProject instance for testing.

        Returns:
            CreateProject: A sample project with fake data
        """

        class CreateProjectFactory(ModelFactory[CreateProject]):
            __model__ = CreateProject
            __faker__ = faker

            name = faker.catch_phrase()
            default_start_url = faker.url()

        element = CreateProjectFactory.build()

        return element


class UpdateProject(UpdateModel):
    """
    Schema for updating an existing project.

    Allows updating the name and default start URL, and automatically
    updates the timestamp when modified.

    Attributes:
        name: Updated name for the project
        default_start_url: Updated default URL where tests start
    """

    name: Optional[str] = None
    default_start_url: Optional[str] = None

    @classmethod
    def sample_factory_build(cls) -> "UpdateProject":
        """
        Generate a sample UpdateProject instance for testing.

        Returns:
            UpdateProject: A sample update project with fake data
        """

        class UpdateProjectFactory(ModelFactory[UpdateProject]):
            __model__ = UpdateProject
            __faker__ = faker

            name = faker.catch_phrase()
            default_start_url = faker.url()

        element = UpdateProjectFactory.build()

        return element


class ResponseProject(BaseModel):
    """
    Schema for project responses returned by the API.

    Contains all project fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning project data to clients.

    Attributes:
        id: Unique project identifier
        created_at: Timestamp when project was created
        name: Human-readable name for the project
        default_start_url: Default URL where tests for this project start
    """

    id: str
    created_at: datetime
    name: str
    default_start_url: str

    @classmethod
    def sample_factory_build(cls, id: str = CUID().generate()) -> "ResponseProject":
        """
        Generate a sample ResponseProject instance for testing.

        Args:
            id: Project ID to use in the sample

        Returns:
            ResponseProject: A sample response project with fake data
        """

        class ResponseProjectFactory(ModelFactory[ResponseProject]):
            __model__ = ResponseProject
            __faker__ = faker

            name = faker.catch_phrase()
            default_start_url = faker.url()

        element = ResponseProjectFactory.build()
        element.id = id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample projects
    rich_print(CreateProject.sample_factory_build())
    rich_print(UpdateProject.sample_factory_build())
    rich_print(ResponseProject.sample_factory_build())
