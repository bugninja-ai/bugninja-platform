"""
SecretValue-TestTraversal association table using SQLModel.

This module defines the association table for the many-to-many relationship
between SecretValue and TestTraversal entities.
"""

from __future__ import annotations


from sqlmodel import Field, SQLModel


class SecretValueTestTraversal(SQLModel, table=True):
    """
    Association table for SecretValue and TestTraversal many-to-many relationship.

    This table connects secret values to test traversals, allowing multiple
    secret values to be used in a single test traversal and multiple test
    traversals to use the same secret values.
    """

    # Foreign keys (composite primary key)
    secret_value_id: str = Field(primary_key=True, max_length=255, foreign_key="secretvalue.id")
    test_traversal_id: str = Field(primary_key=True, max_length=255, foreign_key="testtraversal.id")
