"""
Test Case Communication Schemas

This module defines Pydantic models for test case-related communication responses.
These schemas are used for API responses that include detailed test case information.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.crud.document import ResponseDocument


class ExtendedResponseTestcase(BaseModel):
    """
    Extended test case response with comprehensive details.

    Contains full test case information including associated document
    and detailed configuration. Used for comprehensive test case data retrieval.

    Attributes:
        id: Unique test case identifier
        project_id: Reference to the project this test case belongs to
        document: Optional associated document with full details
        created_at: Timestamp when test case was created
        updated_at: Timestamp when test case was last updated
        test_name: Human-readable name for the test case
        test_description: Detailed description of what the test case does
        test_goal: Specific objective or goal of this test case
        extra_rules: Additional rules or constraints for the test
        url_routes: The URL route/path that this test case targets
        allowed_domains: List of domains that are allowed for this test case
    """

    id: str
    project_id: str
    document: Optional[ResponseDocument]
    created_at: datetime
    updated_at: datetime
    test_name: str
    test_description: str
    test_goal: str
    extra_rules: str
    url_routes: str
    allowed_domains: List[str]
