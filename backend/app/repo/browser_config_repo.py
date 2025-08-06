"""
Browser Config Repository

This module provides static methods for CRUD operations on BrowserConfig entities.
All methods work with the provided database session and use SQLModel table definitions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cuid2 import Cuid as CUID
from sqlmodel import Session, col, select

from app.db.browser_config import BrowserConfig
from app.db.test_traversal import TestTraversal
from app.schemas.crud.browser_config import (
    CreateBrowserConfig,
    UpdateBrowserConfig,
    UpdateBrowserConfigWithId,
)
from app.schemas.crud.test_traversal import CreateTestTraversal


class BrowserConfigRepo:
    """
    Repository class for BrowserConfig entity CRUD operations.

    All methods are static and require a database session to be provided.
    """

    @staticmethod
    def create(db: Session, browser_config_data: CreateBrowserConfig) -> BrowserConfig:
        """
        Create a new browser configuration in the database and create a test traversal for it.

        Args:
            db: Database session
            browser_config_data: Browser configuration creation data

        Returns:
            BrowserConfig: The created browser configuration instance
        """
        # Lazy import to avoid circular dependency
        from app.repo.test_case_repo import TestCaseRepo

        # Get the test case to retrieve the project_id
        test_case = TestCaseRepo.get_by_id(db, browser_config_data.test_case_id)
        if not test_case:
            raise ValueError(f"Test case with id {browser_config_data.test_case_id} not found")

        browser_config = BrowserConfig(
            id=CUID().generate(),
            project_id=test_case.project_id,
            browser_config=browser_config_data.browser_config,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(browser_config)
        db.commit()
        db.refresh(browser_config)

        # Create a test traversal for this browser config
        BrowserConfigRepo._create_test_traversal_for_browser_config(db, browser_config)

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

        for k, v in browser_config_data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(browser_config, k, v)

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

    @staticmethod
    def _create_test_traversal_for_browser_config(
        db: Session, browser_config: BrowserConfig
    ) -> Optional[TestTraversal]:
        """
        Create a test traversal for a browser configuration.

        Args:
            db: Database session
            browser_config: The browser configuration to create a traversal for

        Returns:
            Optional[TestTraversal]: The created test traversal if successful, None otherwise
        """
        try:
            # Lazy imports to avoid circular dependency
            from app.repo.test_case_repo import TestCaseRepo
            from app.repo.test_traversal_repo import TestTraversalRepo

            # Get test cases for the same project
            test_cases = TestCaseRepo.get_by_project_id(
                db, browser_config.project_id, skip=0, limit=10
            )

            if not test_cases:
                # No test cases available for this project, skip traversal creation
                return None

            # Use the first test case for the traversal
            test_case = test_cases[0]

            # Generate traversal name based on browser config and test case
            browser_type = browser_config.browser_config.get("browser", "Unknown")
            traversal_name = f"Traversal - {test_case.test_name} ({browser_type})"

            # Create test traversal data
            test_traversal_data = CreateTestTraversal(
                test_case_id=test_case.id,
                browser_config_id=browser_config.id,
                traversal_name=traversal_name,
            )

            # Create the test traversal
            test_traversal = TestTraversalRepo.create(db, test_traversal_data)

            return test_traversal

        except Exception as e:
            # Log error but don't fail the browser config creation
            print(
                f"Warning: Failed to create test traversal for browser config {browser_config.id}: {e}"
            )
            return None

    @staticmethod
    def create_with_traversal(
        db: Session, browser_config_data: CreateBrowserConfig
    ) -> BrowserConfig:
        """
        Create a new browser configuration and automatically create a test traversal.

        Args:
            db: Database session
            browser_config_data: Browser configuration creation data

        Returns:
            BrowserConfig: The created browser configuration instance
        """
        # Lazy import to avoid circular dependency
        from app.repo.test_case_repo import TestCaseRepo

        # Get the test case to retrieve the project_id
        test_case = TestCaseRepo.get_by_id(db, browser_config_data.test_case_id)
        if not test_case:
            raise ValueError(f"Test case with id {browser_config_data.test_case_id} not found")

        browser_config = BrowserConfig(
            id=CUID().generate(),
            project_id=test_case.project_id,
            browser_config=browser_config_data.browser_config,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(browser_config)
        db.commit()
        db.refresh(browser_config)

        # Create a test traversal for this browser config using the specified test case
        BrowserConfigRepo._create_test_traversal_with_specific_test_case(
            db, browser_config, browser_config_data.test_case_id
        )

        return browser_config

    @staticmethod
    def _create_test_traversal_with_specific_test_case(
        db: Session, browser_config: BrowserConfig, test_case_id: str
    ) -> Optional[TestTraversal]:
        """
        Create a test traversal for a browser configuration with a specific test case.

        Args:
            db: Database session
            browser_config: The browser configuration to create a traversal for
            test_case_id: The specific test case ID to use

        Returns:
            Optional[TestTraversal]: The created test traversal if successful, None otherwise
        """
        try:
            # Lazy imports to avoid circular dependency
            from app.repo.test_case_repo import TestCaseRepo
            from app.repo.test_traversal_repo import TestTraversalRepo

            # Get the specific test case
            test_case = TestCaseRepo.get_by_id(db, test_case_id)

            if not test_case:
                print(f"Warning: Test case {test_case_id} not found")
                return None

            # Verify the test case belongs to the same project
            if test_case.project_id != browser_config.project_id:
                print(
                    f"Warning: Test case {test_case_id} does not belong to the same project as browser config"
                )
                return None

            # Generate traversal name based on browser config and test case
            browser_type = browser_config.browser_config.get("browser", "Unknown")
            traversal_name = f"Traversal - {test_case.test_name} ({browser_type})"

            # Create test traversal data
            test_traversal_data = CreateTestTraversal(
                test_case_id=test_case.id,
                browser_config_id=browser_config.id,
                traversal_name=traversal_name,
            )

            # Create the test traversal
            test_traversal = TestTraversalRepo.create(db, test_traversal_data)

            return test_traversal

        except Exception as e:
            # Log error but don't fail the browser config creation
            print(
                f"Warning: Failed to create test traversal for browser config {browser_config.id}: {e}"
            )
            return None

    @staticmethod
    def bulk_create_with_traversals(
        db: Session,
        browser_configs_data: List[CreateBrowserConfig],
    ) -> Tuple[List[BrowserConfig], List[Dict[str, Any]]]:
        """
        Create multiple browser configurations with test traversals.

        Args:
            db: Database session
            browser_configs_data: List of browser configuration creation data

        Returns:
            Tuple containing:
            - List of created browser configurations
            - List of failed creations with error details
        """
        created_browser_configs = []
        failed_creations = []

        # Lazy import to avoid circular dependency
        from app.repo.test_case_repo import TestCaseRepo
        from app.repo.test_traversal_repo import TestTraversalRepo

        # Process each browser config
        for index, browser_config_data in enumerate(browser_configs_data):
            try:
                # Validate that the referenced test case exists
                test_case = TestCaseRepo.get_by_id(db, browser_config_data.test_case_id)
                if not test_case:
                    failed_creations.append(
                        {
                            "index": index,
                            "error": f"Test case with id {browser_config_data.test_case_id} not found",
                            "data": browser_config_data.model_dump(),
                        }
                    )
                    continue

                # Create browser config
                browser_config = BrowserConfig(
                    id=CUID().generate(),
                    project_id=test_case.project_id,
                    browser_config=browser_config_data.browser_config,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(browser_config)
                db.flush()  # Flush to get the ID

                # Create test traversal for this browser config
                browser_type = browser_config.browser_config.get("browser", "Unknown")

                TestTraversalRepo.create(
                    db,
                    CreateTestTraversal(
                        test_case_id=test_case.id,
                        browser_config_id=browser_config.id,
                        traversal_name=f"Traversal - {test_case.test_name} ({browser_type})",
                    ),
                )

                created_browser_configs.append(browser_config)

            except Exception as e:
                failed_creations.append(
                    {
                        "index": index,
                        "error": str(e),
                        "data": browser_config_data.model_dump(),
                    }
                )

        # Commit all successful creations
        if created_browser_configs:
            db.commit()

        return created_browser_configs, failed_creations

    @staticmethod
    def bulk_update(
        db: Session,
        browser_configs_data: List[UpdateBrowserConfigWithId],
        new_browser_configs: List[CreateBrowserConfig] = [],
        existing_browser_config_ids_to_add: List[str] = [],
        browser_config_ids_to_unlink: List[str] = [],
        test_case_id: Optional[str] = None,
    ) -> Tuple[
        List[BrowserConfig],
        List[BrowserConfig],
        List[BrowserConfig],
        int,
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
    ]:
        """
        Perform bulk operations on browser configurations: update, create, link existing, and unlink.

        Args:
            db: Database session
            browser_configs_data: List of browser configuration update data with IDs
            new_browser_configs: List of new browser configurations to create
            existing_browser_config_ids_to_add: List of existing browser config IDs to link to test case
            browser_config_ids_to_unlink: List of browser config IDs to unlink from test case
            test_case_id: Test case ID for creating new configs, linking existing, and unlinking

        Returns:
            Tuple containing:
            - List of updated browser configurations
            - List of created browser configurations
            - List of linked existing browser configurations
            - Number of unlinked browser configurations
            - List of failed updates with error details
            - List of failed creations with error details
            - List of failed link attempts with error details
        """
        updated_browser_configs = []
        created_browser_configs = []
        linked_browser_configs = []
        failed_updates = []
        failed_creations = []
        failed_links = []
        total_unlinked = 0

        # Lazy import to avoid circular dependency
        from app.repo.test_case_repo import TestCaseRepo

        # 1. Handle updates to existing browser configs
        for index, browser_config_data in enumerate(browser_configs_data):
            try:
                # Check if browser config exists
                existing_browser_config = BrowserConfigRepo.get_by_id(db, browser_config_data.id)
                if not existing_browser_config:
                    failed_updates.append(
                        {
                            "index": index,
                            "error": f"Browser config with id {browser_config_data.id} not found",
                            "data": browser_config_data.model_dump(),
                        }
                    )
                    continue

                # Update browser config fields
                update_data = browser_config_data.model_dump(
                    exclude_unset=True, exclude_none=True, exclude={"id"}
                )

                for field, value in update_data.items():
                    setattr(existing_browser_config, field, value)

                # Update timestamp
                existing_browser_config.updated_at = datetime.now(timezone.utc)

                db.add(existing_browser_config)
                updated_browser_configs.append(existing_browser_config)

            except Exception as e:
                failed_updates.append(
                    {
                        "index": index,
                        "error": str(e),
                        "data": browser_config_data.model_dump(),
                    }
                )

        # 2. Handle creation of new browser configs
        if new_browser_configs and test_case_id:
            for index, browser_config_data in enumerate(new_browser_configs):
                try:
                    # Set the test case ID for the new browser config
                    browser_config_data.test_case_id = test_case_id

                    # Create the browser config
                    new_browser_config = BrowserConfigRepo.create(db, browser_config_data)
                    created_browser_configs.append(new_browser_config)

                    # Create the association between test case and browser config
                    # This is crucial - without this, the browser config won't appear in the test case
                    TestCaseRepo._associate_browser_configs_with_test_case(
                        db, test_case_id, [new_browser_config.id]
                    )

                except Exception as e:
                    failed_creations.append(
                        {
                            "index": index,
                            "error": str(e),
                            "data": browser_config_data.model_dump(),
                        }
                    )

        # 3. Handle linking existing browser configs to test case
        if existing_browser_config_ids_to_add and test_case_id:
            for index, browser_config_id in enumerate(existing_browser_config_ids_to_add):
                try:
                    # Get the existing browser config
                    existing_browser_config = BrowserConfigRepo.get_by_id(db, browser_config_id)
                    if not existing_browser_config:
                        failed_links.append(
                            {
                                "index": index,
                                "error": f"Browser config with ID {browser_config_id} not found",
                                "browser_config_id": browser_config_id,
                            }
                        )
                        continue

                    # Create association between test case and browser config
                    TestCaseRepo._associate_browser_configs_with_test_case(
                        db, test_case_id, [browser_config_id]
                    )

                    # Create test traversal for this browser config and test case
                    BrowserConfigRepo._create_test_traversal_with_specific_test_case(
                        db, existing_browser_config, test_case_id
                    )

                    linked_browser_configs.append(existing_browser_config)

                except Exception as e:
                    failed_links.append(
                        {
                            "index": index,
                            "error": str(e),
                            "browser_config_id": browser_config_id,
                        }
                    )

        # 4. Handle unlinking browser configs from test case
        if browser_config_ids_to_unlink and test_case_id:
            try:
                # Use the existing method from TestCaseRepo to unlink
                TestCaseRepo._remove_browser_config_associations(
                    db, test_case_id, browser_config_ids_to_unlink
                )
                total_unlinked = len(browser_config_ids_to_unlink)
            except Exception as e:
                # If unlinking fails, we'll add it to failed updates
                failed_updates.append(
                    {
                        "operation": "unlink",
                        "error": str(e),
                        "browser_config_ids": browser_config_ids_to_unlink,
                    }
                )

        # Commit all successful operations
        if (
            updated_browser_configs
            or created_browser_configs
            or linked_browser_configs
            or total_unlinked > 0
        ):
            db.commit()

        return (
            updated_browser_configs,
            created_browser_configs,
            linked_browser_configs,
            total_unlinked,
            failed_updates,
            failed_creations,
            failed_links,
        )
