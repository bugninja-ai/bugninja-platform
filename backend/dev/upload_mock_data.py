"""
Mock Data Upload Script

This script creates a comprehensive set of mock data for testing the application.
It creates a complete hierarchy of entities with proper relationships:
- 1 Project
- 1 Document
- 3 Test Cases (one connected to document)
- 3 Browser Configs
- 5 Secret Values
- 9 Test Traversals (3×3 cross product)
- 27 Brain States (3 per traversal)
- 81 Actions (3 per brain state)
- 1 Test Run (for first traversal)
- 1 Cost record
- 9 History Elements (one per action in test run)
- 2 Test Traversals linked to all 5 Secret Values
- TestCase-BrowserConfig associations
"""

from typing import List

from rich import print as rich_print

from app.db.base import QuinoContextManager
from app.db.browser_config import BrowserConfig
from app.db.secret_value import SecretValue
from app.db.secret_value_test_traversal import SecretValueTestTraversal
from app.db.test_case import TestCase
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_traversal import TestTraversal
from app.repo import (
    ActionRepo,
    BrainStateRepo,
    BrowserConfigRepo,
    CostRepo,
    DocumentRepo,
    HistoryElementRepo,
    ProjectRepo,
    SecretValueRepo,
    TestCaseRepo,
    TestRunRepo,
    TestTraversalRepo,
)
from app.schemas.crud.action import CreateAction
from app.schemas.crud.brain_state import CreateBrainState
from app.schemas.crud.browser_config import CreateBrowserConfig
from app.schemas.crud.cost import CreateCost
from app.schemas.crud.document import CreateDocument
from app.schemas.crud.history_element import CreateHistoryElement
from app.schemas.crud.project import CreateProject
from app.schemas.crud.secret_value import CreateSecretValue
from app.schemas.crud.test_case import CreateTestCase
from app.schemas.crud.test_run import CreateTestRun
from app.schemas.crud.test_traversal import CreateTestTraversal


def upload_mock_data() -> None:
    """
    Upload comprehensive mock data to the database.

    Creates a complete test dataset with all required relationships
    and proper foreign key constraints.

    Raises:
        RuntimeError: If there are existing projects in the database
    """
    with QuinoContextManager() as db:
        try:
            rich_print("Starting mock data upload...")

            # Check if there are existing projects
            existing_projects = ProjectRepo.get_all(db)
            if not existing_projects:

                rich_print("✓ Database is empty, proceeding with mock data upload...")

                # Phase 1: Core entities (Project, Document, BrowserConfig, SecretValue)
                rich_print("Creating core entities...")

                # Create Project
                project = ProjectRepo.create(db, CreateProject.sample_factory_build())
                rich_print(f"✓ Created project: {project.name}")
                db.commit()

                # Create Document
                document = DocumentRepo.create(db, CreateDocument.sample_factory_build(project.id))
                rich_print(f"✓ Created document: {document.name}")
                db.commit()

                # Create 3 Browser Configs
                browser_configs: List[BrowserConfig] = []
                for i in range(3):
                    browser_config = BrowserConfigRepo.create(
                        db, CreateBrowserConfig.sample_factory_build(project.id)
                    )
                    browser_configs.append(browser_config)
                    rich_print(f"✓ Created browser config {i+1}")
                db.commit()

                # Create 5 Secret Values
                secret_values: List[SecretValue] = []
                for i in range(5):
                    secret_value = SecretValueRepo.create(
                        db, CreateSecretValue.sample_factory_build(project.id)
                    )
                    secret_values.append(secret_value)
                    rich_print(f"✓ Created secret value {i+1}: {secret_value.secret_name}")

                # Commit Phase 1 to ensure IDs are available
                db.commit()
                rich_print("✓ Committed Phase 1 entities")

                # Phase 2: Test Cases
                rich_print("Creating test cases...")

                # Create 3 Test Cases (first one with document_id)
                test_cases: List[TestCase] = []
                for i in range(3):
                    document_id = document.id if i == 0 else None
                    test_case = TestCaseRepo.create(
                        db, CreateTestCase.sample_factory_build(project.id, document_id)
                    )
                    test_cases.append(test_case)
                    rich_print(f"✓ Created test case {i+1}: {test_case.test_name}")

                db.commit()
                # Create TestCase-BrowserConfig associations (many-to-many)
                rich_print("Creating test case - browser config associations...")
                for test_case in test_cases:
                    for browser_config in browser_configs:
                        association = TestCaseBrowserConfig(
                            test_case_id=test_case.id, browser_config_id=browser_config.id
                        )
                        db.add(association)
                        rich_print(f"✓ Linked test case '{test_case.test_name}' to browser config")

                # Commit Phase 2
                db.commit()
                rich_print("✓ Committed Phase 2 entities")

                # Phase 3: Test Traversals
                rich_print("Creating test traversals...")

                # Create 9 Test Traversals (3×3 cross product)
                traversals: List[TestTraversal] = []
                for i, test_case in enumerate(test_cases):
                    for j, browser_config in enumerate(browser_configs):
                        traversal = TestTraversalRepo.create(
                            db,
                            CreateTestTraversal.sample_factory_build(
                                test_case.id, browser_config.id
                            ),
                        )
                        traversals.append(traversal)
                        rich_print(
                            f"✓ Created traversal {len(traversals)}: {traversal.traversal_name}"
                        )

                db.commit()
                # Link first 2 traversals to all 5 secret values
                rich_print("Linking secret values to traversals...")
                for i, traversal in enumerate(traversals[:2]):
                    for secret_value in secret_values:
                        link = SecretValueTestTraversal(
                            secret_value_id=secret_value.id, test_traversal_id=traversal.id
                        )
                        db.add(link)
                        rich_print(
                            f"✓ Linked secret '{secret_value.secret_name}' to traversal {i+1}"
                        )

                # Commit Phase 3
                db.commit()
                rich_print("✓ Committed Phase 3 entities")

                # Phase 4: Brain states and actions
                rich_print("Creating brain states and actions...")

                brain_states = []
                actions = []

                for traversal_idx, traversal in enumerate(traversals):
                    for brain_state_idx in range(3):
                        brain_state = BrainStateRepo.create(
                            db, CreateBrainState.sample_factory_build(traversal.id, brain_state_idx)
                        )
                        brain_states.append(brain_state)

                        for action_idx in range(3):
                            action = ActionRepo.create(
                                db, CreateAction.sample_factory_build(brain_state.id, action_idx)
                            )
                            actions.append(action)

                            # Print progress for first traversal only to avoid spam
                            if traversal_idx == 0:
                                rich_print(
                                    f"✓ Created action {action_idx+1} for brain state {brain_state_idx+1} in traversal 1"
                                )

                rich_print(f"✓ Created {len(brain_states)} brain states and {len(actions)} actions")

                # Commit Phase 4
                db.commit()
                rich_print("✓ Committed Phase 4 entities")

                # Phase 5: Test execution (first traversal only)
                rich_print("Creating test execution data...")

                # Create Test Run for first traversal
                first_traversal = traversals[0]
                test_run = TestRunRepo.create(
                    db,
                    CreateTestRun.sample_factory_build(
                        first_traversal.id, first_traversal.browser_config_id
                    ),
                )
                rich_print(f"✓ Created test run: {test_run.id}")
                db.commit()

                # Create Cost record for the test run
                cost = CostRepo.create(db, CreateCost.sample_factory_build(test_run.id, project.id))
                rich_print(f"✓ Created cost record: ${cost.cost_in_dollars:.4f}")
                db.commit()

                # Create History Elements for first 9 actions (3 brain states × 3 actions from first traversal)
                first_traversal_actions = actions[:9]  # First 9 actions belong to first traversal
                for i, action in enumerate(first_traversal_actions):
                    HistoryElementRepo.create(
                        db, CreateHistoryElement.sample_factory_build(test_run.id, action.id)
                    )
                    rich_print(f"✓ Created history element {i+1} for action {action.id}")

                # Final commit
                db.commit()

                rich_print("\n🎉 Mock data upload completed successfully!")
                rich_print("📊 Summary:")
                rich_print(f"   • 1 Project: {project.name}")
                rich_print(f"   • 1 Document: {document.name}")
                rich_print("   • 3 Test Cases")
                rich_print("   • 3 Browser Configs")
                rich_print("   • 5 Secret Values")
                rich_print("   • 9 Test Traversals")
                rich_print("   • 27 Brain States")
                rich_print("   • 81 Actions")
                rich_print("   • 1 Test Run")
                rich_print("   • 1 Cost Record")
                rich_print("   • 9 History Elements")
                rich_print("   • 2 Traversals linked to all 5 Secret Values")
                rich_print("   • 9 TestCase-BrowserConfig associations")
            else:
                rich_print(
                    "❌ Error: Database already contains projects. Please clear the database first."
                )
                rich_print(f"   Found {len(existing_projects)} existing project(s):")
                for project in existing_projects:
                    rich_print(f"   • {project.name} (ID: {project.id})")

        except Exception as e:
            rich_print(f"❌ Error during mock data upload: {e}")
            db.rollback()
            raise


if __name__ == "__main__":
    upload_mock_data()
