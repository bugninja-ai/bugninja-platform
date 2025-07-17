"""
SecretValue table definition.

This module defines the SQLAlchemy model for the SecretValue entity.
"""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import DBTableBaseModel
from app.db.project import Project
from app.db.test_run import TestRun


class SecretValue(DBTableBaseModel):
    """
    SecretValue table.

    Secret values store sensitive configuration data for projects such as
    API keys, passwords, and other credentials. Each secret belongs to
    a specific project and should be encrypted at rest.
    """

    __tablename__ = "secret_values"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    project_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Secret information
    secret_name: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_value: Mapped[str] = mapped_column(Text, nullable=False)  # Should be encrypted

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="secret_values")
    test_runs: Mapped[List["TestRun"]] = relationship(
        "TestRun", secondary="secret_value_test_runs", back_populates="secret_values"
    )
