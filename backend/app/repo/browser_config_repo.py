"""
Browser Config Repository

This module provides static methods for CRUD operations on BrowserConfig entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Any, Optional, Sequence

from sqlmodel import Session, col, select

from app.db.browser_config import BrowserConfig
from app.schemas.crud.browser_config import (
    CreateBrowserConfig,
    UpdateBrowserConfig,
)


class BrowserConfigRepo:
    """
    Repository class for BrowserConfig entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, browser_config_data: CreateBrowserConfig) -> BrowserConfig:
        """
        Create a new browser configuration in the database.

        Args:
            db: Database session
            browser_config_data: Browser configuration creation data

        Returns:
            BrowserConfig: The created browser configuration instance
        """
        browser_config = BrowserConfig(
            id=browser_config_data.id,
            project_id=browser_config_data.project_id,
            browser_config=browser_config_data.browser_config,
            created_at=browser_config_data.created_at,
            updated_at=browser_config_data.updated_at,
        )
        db.add(browser_config)
        db.commit()
        db.refresh(browser_config)
        return browser_config

    @staticmethod
    def get_by_id(db: Session, browser_config_id: str) -> Optional[BrowserConfig]:
        """
        Retrieve a browser configuration by its ID.

        Args:
            db: Database session
            browser_config_id: Unique browser configuration identifier

        Returns:
            Optional[BrowserConfig]: The browser configuration if found, None otherwise
        """
        statement = select(BrowserConfig).where(BrowserConfig.id == browser_config_id)
        return db.exec(statement).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Sequence[BrowserConfig]:
        """
        Retrieve all browser configurations with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrowserConfig]: List of browser configurations
        """
        statement = select(BrowserConfig).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def get_by_project_id(
        db: Session, project_id: str, skip: int = 0, limit: int = 100
    ) -> Sequence[BrowserConfig]:
        """
        Retrieve all browser configurations for a specific project.

        Args:
            db: Database session
            project_id: Project identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrowserConfig]: List of browser configurations for the project
        """
        statement = (
            select(BrowserConfig)
            .where(BrowserConfig.project_id == project_id)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def update(
        db: Session, browser_config_id: str, browser_config_data: UpdateBrowserConfig
    ) -> Optional[BrowserConfig]:
        """
        Update an existing browser configuration.

        Args:
            db: Database session
            browser_config_id: Unique browser configuration identifier
            browser_config_data: Browser configuration update data

        Returns:
            Optional[BrowserConfig]: The updated browser configuration if found, None otherwise
        """
        browser_config = BrowserConfigRepo.get_by_id(db, browser_config_id)
        if not browser_config:
            return None

        browser_config.browser_config = browser_config_data.browser_config
        browser_config.updated_at = datetime.now(timezone.utc)

        db.add(browser_config)
        db.commit()
        db.refresh(browser_config)
        return browser_config

    @staticmethod
    def delete(db: Session, browser_config_id: str) -> bool:
        """
        Delete a browser configuration by its ID.

        Args:
            db: Database session
            browser_config_id: Unique browser configuration identifier

        Returns:
            bool: True if browser configuration was deleted, False if not found
        """
        browser_config = BrowserConfigRepo.get_by_id(db, browser_config_id)
        if not browser_config:
            return False

        db.delete(browser_config)
        db.commit()
        return True

    @staticmethod
    def search_by_config_key(
        db: Session, key: str, value: Any, skip: int = 0, limit: int = 100
    ) -> Sequence[BrowserConfig]:
        """
        Search browser configurations by a specific config key and value.

        Args:
            db: Database session
            key: Configuration key to search for
            value: Value to match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrowserConfig]: List of matching browser configurations
        """
        # Note: This is a simplified search. For more complex JSON queries,
        # you might need to use database-specific JSON operators
        statement = (
            select(BrowserConfig)
            .where(col(BrowserConfig.browser_config).contains({key: value}))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_by_browser_type(
        db: Session, browser_type: str, skip: int = 0, limit: int = 100
    ) -> Sequence[BrowserConfig]:
        """
        Retrieve browser configurations by browser type.

        Args:
            db: Database session
            browser_type: Browser type (e.g., 'chrome', 'firefox', 'safari')
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrowserConfig]: List of browser configurations for the specified browser type
        """
        statement = (
            select(BrowserConfig)
            .where(col(BrowserConfig.browser_config).contains({"browser": browser_type}))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def get_headless_configs(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[BrowserConfig]:
        """
        Retrieve browser configurations that are configured for headless mode.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrowserConfig]: List of headless browser configurations
        """
        statement = (
            select(BrowserConfig)
            .where(col(BrowserConfig.browser_config).contains({"headless": True}))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()

    @staticmethod
    def count_by_project(db: Session, project_id: str) -> int:
        """
        Get the total number of browser configurations for a project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Total number of browser configurations for the project
        """
        statement = select(BrowserConfig).where(BrowserConfig.project_id == project_id)
        return len(db.exec(statement).all())

    @staticmethod
    def count(db: Session) -> int:
        """
        Get the total number of browser configurations.

        Args:
            db: Database session

        Returns:
            int: Total number of browser configurations
        """
        statement = select(BrowserConfig)
        return len(db.exec(statement).all())

    @staticmethod
    def delete_by_project(db: Session, project_id: str) -> int:
        """
        Delete all browser configurations for a specific project.

        Args:
            db: Database session
            project_id: Project identifier

        Returns:
            int: Number of browser configurations deleted
        """
        statement = select(BrowserConfig).where(BrowserConfig.project_id == project_id)
        browser_configs = db.exec(statement).all()
        count = len(browser_configs)

        for browser_config in browser_configs:
            db.delete(browser_config)

        db.commit()
        return count

    @staticmethod
    def get_default_configs(
        db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[BrowserConfig]:
        """
        Retrieve browser configurations with common default settings.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Sequence[BrowserConfig]: List of default browser configurations
        """
        # This is a simplified approach. You might want to define specific criteria
        # for what constitutes a "default" configuration
        statement = (
            select(BrowserConfig)
            .where(col(BrowserConfig.browser_config).contains({"headless": True}))
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()
