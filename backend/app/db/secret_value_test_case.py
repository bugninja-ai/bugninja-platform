"""
SecretValue-TestCase association table using SQLModel.

This module defines the association table for the many-to-many relationship
between SecretValue and TestCase entities.
"""

from sqlmodel import Field, SQLModel


class SecretValueTestCase(SQLModel, table=True):
    """
    Association table for SecretValue and TestCase many-to-many relationship.

    This table connects secret values to test cases, allowing multiple
    secret values to be used in a single test case and multiple test
    cases to use the same secret values.
    """

    # Foreign keys (composite primary key)
    secret_value_id: str = Field(primary_key=True, max_length=255, foreign_key="secretvalue.id")
    test_case_id: str = Field(primary_key=True, max_length=255, foreign_key="testcase.id")
