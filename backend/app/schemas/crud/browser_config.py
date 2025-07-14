"""
BrowserConfig CRUD Schemas

This module defines Pydantic models for BrowserConfig entity CRUD operations.
Browser configurations store browser-specific settings and parameters for test execution.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker


class CreateBrowserConfig(CreationModel):
    """
    Schema for creating a new browser configuration.

    Browser configurations store browser-specific settings and parameters
    that can be used during test execution. These configurations are
    reusable across different test cases.

    Attributes:
        id: Unique identifier generated using CUID
        created_at: Timestamp when the browser config was created (UTC)
        updated_at: Timestamp when the browser config was last updated (UTC)
        browser_config: Dictionary containing browser-specific configuration settings
    """

    id: str = Field(default=CUID().generate())
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    browser_config: Dict[str, Any]

    @classmethod
    def sample_factory_build(cls) -> "CreateBrowserConfig":
        """
        Generate a sample CreateBrowserConfig instance for testing.

        Returns:
            CreateBrowserConfig: A sample browser config with fake data
        """

        class CreateBrowserConfigFactory(ModelFactory[CreateBrowserConfig]):
            __model__ = CreateBrowserConfig
            __faker__ = faker

            browser_config = {
                "browser": "chrome",
                "headless": True,
                "viewport": {"width": 1920, "height": 1080},
                "userAgent": faker.user_agent(),
                "timeout": 30000,
                "args": ["--no-sandbox", "--disable-dev-shm-usage"],
            }

        element = CreateBrowserConfigFactory.build()

        return element


class UpdateBrowserConfig(UpdateModel):
    """
    Schema for updating an existing browser configuration.

    Allows updating the browser configuration settings and automatically
    updates the timestamp when modified.

    Attributes:
        updated_at: Automatically updated timestamp when browser config is modified
        browser_config: Updated browser-specific configuration settings
    """

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    browser_config: Dict[str, Any]

    @classmethod
    def sample_factory_build(cls) -> "UpdateBrowserConfig":
        """
        Generate a sample UpdateBrowserConfig instance for testing.

        Returns:
            UpdateBrowserConfig: A sample update browser config with fake data
        """

        class UpdateBrowserConfigFactory(ModelFactory[UpdateBrowserConfig]):
            __model__ = UpdateBrowserConfig
            __faker__ = faker

            browser_config = {
                "browser": "firefox",
                "headless": False,
                "viewport": {"width": 1366, "height": 768},
                "userAgent": faker.user_agent(),
                "timeout": 60000,
                "args": ["--disable-gpu", "--disable-web-security"],
            }

        element = UpdateBrowserConfigFactory.build()

        return element


class ResponseBrowserConfig(BaseModel):
    """
    Schema for browser configuration responses returned by the API.

    Contains all browser config fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning browser config data to clients.

    Attributes:
        id: Unique browser config identifier
        created_at: Timestamp when browser config was created
        updated_at: Timestamp when browser config was last updated
        browser_config: Browser-specific configuration settings
    """

    id: str
    created_at: datetime
    updated_at: datetime
    browser_config: Dict[str, Any]

    @classmethod
    def sample_factory_build(cls, id: str = CUID().generate()) -> "ResponseBrowserConfig":
        """
        Generate a sample ResponseBrowserConfig instance for testing.

        Args:
            id: Browser config ID to use in the sample

        Returns:
            ResponseBrowserConfig: A sample response browser config with fake data
        """

        class ResponseBrowserConfigFactory(ModelFactory[ResponseBrowserConfig]):
            __model__ = ResponseBrowserConfig
            __faker__ = faker

            browser_config = {
                "browser": "safari",
                "headless": True,
                "viewport": {"width": 1440, "height": 900},
                "userAgent": faker.user_agent(),
                "timeout": 45000,
                "args": ["--disable-extensions", "--disable-plugins"],
            }

        element = ResponseBrowserConfigFactory.build()
        element.id = id

        return element


if __name__ == "__main__":
    # Demo: Generate and display sample browser configs
    rich_print(CreateBrowserConfig.sample_factory_build())
    rich_print(UpdateBrowserConfig.sample_factory_build())
    rich_print(ResponseBrowserConfig.sample_factory_build())
