"""
BrowserConfig CRUD Schemas

This module defines Pydantic models for BrowserConfig entity CRUD operations.
Browser configurations store browser-specific settings and parameters for test execution.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cuid2 import Cuid as CUID
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field
from rich import print as rich_print

from app.schemas.crud.base import CreationModel, UpdateModel, faker
from app.schemas.crud.utils import generate_browser_config_data


class CreateBrowserConfig(CreationModel):
    """
    Schema for creating a new browser configuration.

    Browser configurations store browser-specific settings and parameters
    that can be used during test execution. These configurations are
    reusable across different test cases.

    Attributes:
        test_case_id: Reference to the test case this browser config belongs to
        browser_config: Dictionary containing browser-specific configuration settings
    """

    test_case_id: str
    browser_config: Dict[str, Any]

    @classmethod
    def sample_factory_build(cls, test_case_id: str = CUID().generate()) -> "CreateBrowserConfig":
        """
        Generate a sample CreateBrowserConfig instance for testing.

        Args:
            test_case_id: Test case ID that the browser config belongs to

        Returns:
            CreateBrowserConfig: A sample browser config with fake data
        """

        class CreateBrowserConfigFactory(ModelFactory[CreateBrowserConfig]):
            __model__ = CreateBrowserConfig
            __faker__ = faker

            browser_config = generate_browser_config_data(faker, "default")

        element = CreateBrowserConfigFactory.build()
        element.test_case_id = test_case_id

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
    browser_config: Optional[Dict[str, Any]] = None

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

            browser_config = generate_browser_config_data(faker, "alternative")

        element = UpdateBrowserConfigFactory.build()

        return element


class ResponseBrowserConfig(BaseModel):
    """
    Schema for browser configuration responses returned by the API.

    Contains all browser config fields including read-only fields like ID and timestamps.
    Used for GET operations and when returning browser config data to clients.

    Attributes:
        id: Unique browser config identifier
        project_id: Reference to the project this browser config belongs to
        created_at: Timestamp when browser config was created
        updated_at: Timestamp when browser config was last updated
        browser_config: Browser-specific configuration settings
    """

    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    browser_config: Dict[str, Any]

    @classmethod
    def sample_factory_build(
        cls, id: str = CUID().generate(), project_id: str = CUID().generate()
    ) -> "ResponseBrowserConfig":
        """
        Generate a sample ResponseBrowserConfig instance for testing.

        Args:
            id: Browser config ID to use in the sample
            project_id: Project ID that the browser config belongs to

        Returns:
            ResponseBrowserConfig: A sample response browser config with fake data
        """

        class ResponseBrowserConfigFactory(ModelFactory[ResponseBrowserConfig]):
            __model__ = ResponseBrowserConfig
            __faker__ = faker

            browser_config = generate_browser_config_data(faker, "response")

        element = ResponseBrowserConfigFactory.build()
        element.id = id
        element.project_id = project_id

        return element


class BulkCreateBrowserConfigRequest(BaseModel):
    """
    Request schema for bulk browser configuration creation.

    Allows creating multiple browser configurations in a single request
    with automatic test traversal creation for each browser config.

    Attributes:
        browser_configs: List of browser configuration creation data
    """

    browser_configs: List[CreateBrowserConfig]

    @classmethod
    def sample_factory_build(
        cls, test_case_id: str = CUID().generate()
    ) -> "BulkCreateBrowserConfigRequest":
        """
        Generate a sample BulkCreateBrowserConfigRequest instance for testing.

        Args:
            test_case_id: Test case ID to use for creating test traversals

        Returns:
            BulkCreateBrowserConfigRequest: A sample bulk request with fake data
        """
        # Create 3 sample browser configs
        browser_configs = []
        for i in range(3):
            browser_config = CreateBrowserConfig.sample_factory_build(test_case_id)
            browser_configs.append(browser_config)

        return cls(browser_configs=browser_configs)


class BulkCreateBrowserConfigResponse(BaseModel):
    """
    Response schema for bulk browser configuration creation.

    Contains all created browser configurations along with detailed information
    about successful and failed operations.

    Attributes:
        created_browser_configs: List of newly created browser configurations
        total_created: Total number of browser configs successfully created
        failed_creations: List of failed creation attempts with error details
    """

    created_browser_configs: List[ResponseBrowserConfig]
    total_created: int
    failed_creations: List[Dict[str, Any]]

    @classmethod
    def sample_factory_build(
        cls,
        browser_config_count: int = 3,
    ) -> "BulkCreateBrowserConfigResponse":
        """
        Generate a sample BulkCreateBrowserConfigResponse instance for testing.

        Args:
            browser_config_count: Number of browser configs to include

        Returns:
            BulkCreateBrowserConfigResponse: A sample bulk response with fake data
        """
        # Create sample browser configs
        browser_configs = []
        for i in range(browser_config_count):
            browser_config = ResponseBrowserConfig.sample_factory_build()
            browser_configs.append(browser_config)

        return cls(
            created_browser_configs=browser_configs,
            total_created=browser_config_count,
            failed_creations=[],
        )


class UpdateBrowserConfigWithId(BaseModel):
    """
    Schema for updating an existing browser configuration with ID.

    Extends UpdateBrowserConfig with an ID field for bulk operations.

    Attributes:
        id: Unique browser config identifier
        updated_at: Automatically updated timestamp when browser config is modified
        browser_config: Updated browser-specific configuration settings
    """

    id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    browser_config: Optional[Dict[str, Any]] = None

    @classmethod
    def sample_factory_build(cls, id: str = CUID().generate()) -> "UpdateBrowserConfigWithId":
        """
        Generate a sample UpdateBrowserConfigWithId instance for testing.

        Args:
            id: Browser config ID to use in the sample

        Returns:
            UpdateBrowserConfigWithId: A sample update browser config with ID and fake data
        """

        class UpdateBrowserConfigWithIdFactory(ModelFactory[UpdateBrowserConfigWithId]):
            __model__ = UpdateBrowserConfigWithId
            __faker__ = faker

            browser_config = generate_browser_config_data(faker, "alternative")

        element = UpdateBrowserConfigWithIdFactory.build()
        element.id = id

        return element


class BulkUpdateBrowserConfigRequest(BaseModel):
    """
    Request schema for bulk browser configuration updates.

    Allows updating multiple browser configurations in a single request.

    Attributes:
        browser_configs: List of browser configuration update data with IDs
    """

    browser_configs: List[UpdateBrowserConfigWithId]

    @classmethod
    def sample_factory_build(
        cls, browser_config_count: int = 3
    ) -> "BulkUpdateBrowserConfigRequest":
        """
        Generate a sample BulkUpdateBrowserConfigRequest instance for testing.

        Args:
            browser_config_count: Number of browser configs to include

        Returns:
            BulkUpdateBrowserConfigRequest: A sample bulk update request with fake data
        """
        # Create sample browser config updates
        browser_configs = []
        for i in range(browser_config_count):
            browser_config = UpdateBrowserConfigWithId.sample_factory_build()
            browser_configs.append(browser_config)

        return cls(browser_configs=browser_configs)


class BulkUpdateBrowserConfigResponse(BaseModel):
    """
    Response schema for bulk browser configuration updates.

    Contains all updated browser configurations along with detailed information
    about successful and failed operations.

    Attributes:
        updated_browser_configs: List of successfully updated browser configurations
        total_updated: Total number of browser configs successfully updated
        failed_updates: List of failed update attempts with error details
    """

    updated_browser_configs: List[ResponseBrowserConfig]
    total_updated: int
    failed_updates: List[Dict[str, Any]]

    @classmethod
    def sample_factory_build(
        cls, browser_config_count: int = 3
    ) -> "BulkUpdateBrowserConfigResponse":
        """
        Generate a sample BulkUpdateBrowserConfigResponse instance for testing.

        Args:
            browser_config_count: Number of browser configs to include

        Returns:
            BulkUpdateBrowserConfigResponse: A sample bulk update response with fake data
        """
        # Create sample browser configs
        browser_configs = []
        for i in range(browser_config_count):
            browser_config = ResponseBrowserConfig.sample_factory_build()
            browser_configs.append(browser_config)

        return cls(
            updated_browser_configs=browser_configs,
            total_updated=browser_config_count,
            failed_updates=[],
        )


if __name__ == "__main__":
    # Demo: Generate and display sample browser configs
    rich_print(CreateBrowserConfig.sample_factory_build())
    rich_print(UpdateBrowserConfig.sample_factory_build())
    rich_print(ResponseBrowserConfig.sample_factory_build())
    rich_print(BulkCreateBrowserConfigRequest.sample_factory_build())
    rich_print(BulkCreateBrowserConfigResponse.sample_factory_build())
    rich_print(UpdateBrowserConfigWithId.sample_factory_build())
    rich_print(BulkUpdateBrowserConfigRequest.sample_factory_build())
    rich_print(BulkUpdateBrowserConfigResponse.sample_factory_build())
