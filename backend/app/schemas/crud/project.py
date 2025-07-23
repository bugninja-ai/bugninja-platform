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

from app.schemas.crud.base import CreationModel, PaginatedResponse, UpdateModel, faker


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


class PaginatedResponseProject(PaginatedResponse[ResponseProject]):
    """
    Paginated response schema for projects.

    This schema provides a standardized structure for paginated project responses
    with metadata about the pagination state and the actual project items.
    """

    @classmethod
    def sample_factory_build(
        cls, total_count: int = 25, page: int = 1, page_size: int = 10
    ) -> "PaginatedResponseProject":
        """
        Generate a sample PaginatedResponseProject instance for testing and documentation.

        Args:
            total_count: Total number of projects in the database (default: 25)
            page: Page number (1-based, default: 1)
            page_size: Number of records per page (default: 10)

        Returns:
            PaginatedResponseProject: A sample paginated response with fake project data
        """
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
        skip = (page - 1) * page_size
        items_in_page = min(page_size, max(0, total_count - skip))

        # Generate sample project items
        project_items = [ResponseProject.sample_factory_build() for _ in range(items_in_page)]

        # Calculate pagination state
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=project_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )


if __name__ == "__main__":
    # Demo: Generate and display sample projects
    rich_print(CreateProject.sample_factory_build())
    rich_print(UpdateProject.sample_factory_build())
    rich_print(ResponseProject.sample_factory_build())
