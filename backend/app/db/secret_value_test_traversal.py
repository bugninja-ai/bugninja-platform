"""
SecretValue-TestTraversal association table.

This module defines the association table for the many-to-many relationship
between SecretValue and TestTraversal entities.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SecretValueTestTraversal(Base):
    """
    Association table for SecretValue and TestTraversal many-to-many relationship.

    This table connects secret values to test traversals, allowing multiple
    secret values to be used in a single test traversal and multiple test
    traversals to use the same secret values.
    """

    __tablename__ = "secret_value_test_traversals"

    # Foreign keys
    secret_value_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    test_traversal_id: Mapped[str] = mapped_column(String(255), primary_key=True)
