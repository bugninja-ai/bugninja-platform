from typing import Generic, List, TypeVar

from faker import Faker
from pydantic import BaseModel, ConfigDict

faker = Faker()

T = TypeVar("T")


class CreationModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        # TODO! : discuss this with Tomi
        # alias_generator=camelize,
        populate_by_name=True,
    )


class UpdateModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        # TODO! : discuss this with Tomi
        # alias_generator=camelize,
        populate_by_name=True,
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic pagination response model.

    This model provides a standardized structure for paginated API responses
    with metadata about the pagination state and the actual data items.
    """

    items: List[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
