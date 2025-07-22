"""
Base SQLModel for database models.

This module provides the base class for all SQLModel-based database models.
"""

from datetime import datetime, timezone
from typing import Any, Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, Session, SQLModel, create_engine

from app.config import settings

db_engine = create_engine(settings.DATABASE_URL, pool_size=50, max_overflow=50)
# listener = BeforeExecuteFactory(
#     with_db_driver=True,
#     with_db_framework=True,
#     # you may use one of opencensus or opentelemetry
#     with_opentelemetry=True,
# )
# event.listen(db_engine, "before_cursor_execute", listener, retval=True)

# configure_mappers()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine, class_=Session)


class QuinoContextManager:
    def __init__(self) -> None:
        self.db = SessionLocal()

    def __enter__(self) -> Session:
        return self.db

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.db.close()


# Dependency
def get_db() -> Generator[Session, None, None]:
    with QuinoContextManager() as db:
        yield db


class TimestampedModel(SQLModel):
    """
    Base model with timestamp fields.

    Provides common timestamp fields that most models need.
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)


# Import all models to ensure they are registered with SQLModel
# Note: These imports are moved to __init__.py to avoid circular imports

__all__ = [
    "TimestampedModel",
]
