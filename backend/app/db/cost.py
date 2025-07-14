"""
Cost table definition.

This module defines the SQLAlchemy model for the Cost entity.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.project import Project
from app.db.test_run import TestRun


class Cost(Base):
    """
    Cost table.

    Cost records track AI model usage costs and token consumption for test runs.
    Each cost record is associated with a specific test run and project,
    tracking the financial impact of AI-powered testing.
    """

    __tablename__ = "costs"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    test_run_id: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Cost information
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    cost_per_token: Mapped[float] = mapped_column(Float, nullable=False)
    input_token_num: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_token_num: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_in_dollars: Mapped[float] = mapped_column(Float, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="cost")
    project: Mapped["Project"] = relationship("Project", back_populates="costs")
