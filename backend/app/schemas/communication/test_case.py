"""
Test Case Communication Schemas

This module defines Pydantic models for test case-related communication responses.
These schemas are used for API responses that include detailed test case information.
"""

from datetime import datetime
from typing import List, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from rich import print as rich_print

from app.db.test_case import TestCasePriority
from app.schemas.crud.base import faker
from app.schemas.crud.browser_config import ResponseBrowserConfig
from app.schemas.crud.document import ResponseDocument


class ExtendedResponseTestcase(BaseModel):
    """
    Extended test case response with comprehensive details.

    Contains full test case information including associated document,
    browser configurations, and detailed configuration. Used for comprehensive
    test case data retrieval.

    Attributes:
        id: Unique test case identifier
        project_id: Reference to the project this test case belongs to
        document: Optional associated document with full details
        browser_configs: List of associated browser configurations
        created_at: Timestamp when test case was created
        updated_at: Timestamp when test case was last updated
        test_name: Human-readable name for the test case
        test_description: Detailed description of what the test case does
        test_goal: Specific objective or goal of this test case
        extra_rules: Additional rules or constraints for the test
        url_routes: The URL route/path that this test case targets
        allowed_domains: List of domains that are allowed for this test case
        priority: Priority level of the test case
        category: Category for organizing test cases
    """

    id: str
    project_id: str
    document: Optional[ResponseDocument]
    browser_configs: List[ResponseBrowserConfig]
    created_at: datetime
    updated_at: datetime
    test_name: str
    test_description: str
    test_goal: str
    extra_rules: str
    url_routes: str
    allowed_domains: List[str]
    priority: TestCasePriority
    category: Optional[str]

    @classmethod
    def sample_factory_build(
        cls,
        id: str = CUID().generate(),
        project_id: str = CUID().generate(),
        include_document: bool = True,
        include_browser_configs: bool = True,
    ) -> "ExtendedResponseTestcase":
        """
        Generate a sample ExtendedResponseTestcase instance for testing.

        Args:
            id: Test case ID to use in the sample
            project_id: Project ID to use in the sample
            include_document: Whether to include a sample document
            include_browser_configs: Whether to include sample browser configs

        Returns:
            ExtendedResponseTestcase: A sample extended test case response with fake data
        """

        class ExtendedResponseTestcaseFactory(ModelFactory[ExtendedResponseTestcase]):
            __model__ = ExtendedResponseTestcase
            __faker__ = faker

            test_name = faker.catch_phrase()
            test_description = faker.paragraph(nb_sentences=3)
            test_goal = faker.sentence()
            extra_rules = faker.paragraph(nb_sentences=2)
            url_routes = faker.url()
            allowed_domains = [faker.domain_name() for _ in range(3)]
            priority = faker.random_element(
                [
                    TestCasePriority.LOW,
                    TestCasePriority.MEDIUM,
                    TestCasePriority.HIGH,
                    TestCasePriority.CRITICAL,
                ]
            )
            category = faker.random_element(
                ["login", "payment", "search", "navigation", "profile", "settings", "general"]
            )

        element = ExtendedResponseTestcaseFactory.build()
        element.id = id
        element.project_id = project_id

        # Generate optional document
        if include_document:
            element.document = ResponseDocument.sample_factory_build(project_id=project_id)
        else:
            element.document = None

        # Generate optional browser configs
        if include_browser_configs:
            element.browser_configs = [
                ResponseBrowserConfig.sample_factory_build(project_id=project_id)
                for _ in range(faker.random_int(min=1, max=3))
            ]
        else:
            element.browser_configs = []

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample communication schemas
    rich_print("=== ExtendedResponseTestcase Sample (with document and browser configs) ===")
    rich_print(ExtendedResponseTestcase.sample_factory_build())

    rich_print("\n=== ExtendedResponseTestcase Sample (without document) ===")
    rich_print(ExtendedResponseTestcase.sample_factory_build(include_document=False))

    rich_print("\n=== ExtendedResponseTestcase Sample (without browser configs) ===")
    rich_print(ExtendedResponseTestcase.sample_factory_build(include_browser_configs=False))
