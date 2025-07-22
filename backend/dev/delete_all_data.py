"""
Delete All Data Script

This script deletes all data from the database across all tables.
Use this script to clear the database before uploading mock data.

⚠️  WARNING: This will permanently delete ALL data from the database!
"""

import argparse
import sys
from typing import List

from rich import print as rich_print
from sqlalchemy import text

from app.db.base import QuinoContextManager
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


def confirm_deletion(force: bool = False) -> bool:
    """
    Ask for user confirmation before deleting all data.

    Args:
        force: If True, skip confirmation and proceed with deletion

    Returns:
        bool: True if user confirms or force is True, False otherwise
    """
    if force:
        rich_print("⚠️  WARNING: Force mode enabled - proceeding without confirmation!")
        return True

    rich_print("⚠️  WARNING: This will permanently delete ALL data from the database!")
    rich_print("This action cannot be undone.")
    rich_print()

    try:
        while True:
            response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
            if response in ["yes", "y"]:
                return True
            elif response in ["no", "n"]:
                return False
            else:
                rich_print("Please enter 'yes' or 'no'.")
    except EOFError:
        rich_print("❌ Error: Cannot read input. Use --force flag to skip confirmation.")
        return False


def get_table_counts(db) -> List[tuple]:
    """
    Get the count of records in each table.

    Args:
        db: Database session

    Returns:
        List of tuples containing (table_name, count)
    """
    counts = []

    # Count projects (root entity)
    project_count = ProjectRepo.count(db)
    counts.append(("Projects", project_count))

    # Count other entities
    document_count = DocumentRepo.count(db)
    counts.append(("Documents", document_count))

    test_case_count = TestCaseRepo.count(db)
    counts.append(("Test Cases", test_case_count))

    browser_config_count = BrowserConfigRepo.count(db)
    counts.append(("Browser Configs", browser_config_count))

    secret_value_count = SecretValueRepo.count(db)
    counts.append(("Secret Values", secret_value_count))

    test_traversal_count = TestTraversalRepo.count(db)
    counts.append(("Test Traversals", test_traversal_count))

    brain_state_count = BrainStateRepo.count(db)
    counts.append(("Brain States", brain_state_count))

    action_count = ActionRepo.count(db)
    counts.append(("Actions", action_count))

    test_run_count = TestRunRepo.count(db)
    counts.append(("Test Runs", test_run_count))

    history_element_count = HistoryElementRepo.count(db)
    counts.append(("History Elements", history_element_count))

    cost_count = CostRepo.count(db)
    counts.append(("Costs", cost_count))

    return counts


def delete_all_data(force: bool = False) -> None:
    """
    Delete all data from the database across all tables.

    This function deletes data in the correct order to respect foreign key constraints.
    """
    with QuinoContextManager() as db:
        try:
            rich_print("Checking current database state...")

            # Get current counts
            counts = get_table_counts(db)
            total_records = sum(count for _, count in counts)

            if total_records == 0:
                rich_print("✓ Database is already empty.")
                return

            rich_print(f"Current database contains {total_records} records:")
            for table_name, count in counts:
                if count > 0:
                    rich_print(f"   • {table_name}: {count}")

            rich_print()

            # Ask for confirmation
            if not confirm_deletion(force=force):
                rich_print("Operation cancelled.")
                return

            rich_print("🗑️  Starting data deletion...")

            # Delete in order to respect foreign key constraints
            # Start with entities that have no dependencies

            # 1. Delete History Elements (depends on TestRun and Action)
            rich_print("Deleting history elements...")
            history_elements = HistoryElementRepo.get_all(db)
            for history_element in history_elements:
                HistoryElementRepo.delete(db, history_element.id)
            rich_print(f"✓ Deleted {len(history_elements)} history elements")

            # 2. Delete Costs (depends on TestRun and Project)
            rich_print("Deleting costs...")
            costs = CostRepo.get_all(db)
            for cost in costs:
                CostRepo.delete(db, cost.id)
            rich_print(f"✓ Deleted {len(costs)} costs")

            # 3. Delete Actions (depends on BrainState)
            rich_print("Deleting actions...")
            actions = ActionRepo.get_all(db)
            for action in actions:
                ActionRepo.delete(db, action.id)
            rich_print(f"✓ Deleted {len(actions)} actions")

            # 4. Delete Brain States (depends on TestTraversal)
            rich_print("Deleting brain states...")
            brain_states = BrainStateRepo.get_all(db)
            for brain_state in brain_states:
                BrainStateRepo.delete(db, brain_state.id)
            rich_print(f"✓ Deleted {len(brain_states)} brain states")

            # 5. Delete Test Runs (depends on TestTraversal and BrowserConfig)
            rich_print("Deleting test runs...")
            test_runs = TestRunRepo.get_all(db)
            for test_run in test_runs:
                TestRunRepo.delete(db, test_run.id)
            rich_print(f"✓ Deleted {len(test_runs)} test runs")

            # 6. Delete Test Traversals (depends on TestCase and BrowserConfig)
            rich_print("Deleting test traversals...")
            test_traversals = TestTraversalRepo.get_all(db)
            for test_traversal in test_traversals:
                TestTraversalRepo.delete(db, test_traversal.id)
            rich_print(f"✓ Deleted {len(test_traversals)} test traversals")

            # 6.5. Delete Association Tables (must be deleted before main entities)
            rich_print("Deleting association table entries...")

            # Delete TestCaseBrowserConfig associations using direct SQL
            result = db.exec(text("DELETE FROM testcasebrowserconfig"))
            rich_print(f"✓ Deleted {result.rowcount} test case - browser config associations")

            # Delete SecretValueTestTraversal associations using direct SQL
            result = db.exec(text("DELETE FROM secretvaluetesttraversal"))
            rich_print(f"✓ Deleted {result.rowcount} secret value - test traversal associations")

            # 7. Delete Test Cases (depends on Project and Document)
            rich_print("Deleting test cases...")
            test_cases = TestCaseRepo.get_all(db)
            for test_case in test_cases:
                TestCaseRepo.delete(db, test_case.id)
            rich_print(f"✓ Deleted {len(test_cases)} test cases")

            # 8. Delete Browser Configs (depends on Project)
            rich_print("Deleting browser configs...")
            browser_configs = BrowserConfigRepo.get_all(db)
            for browser_config in browser_configs:
                BrowserConfigRepo.delete(db, browser_config.id)
            rich_print(f"✓ Deleted {len(browser_configs)} browser configs")

            # 9. Delete Secret Values (depends on Project)
            rich_print("Deleting secret values...")
            secret_values = SecretValueRepo.get_all(db)
            for secret_value in secret_values:
                SecretValueRepo.delete(db, secret_value.id)
            rich_print(f"✓ Deleted {len(secret_values)} secret values")

            # 10. Delete Documents (depends on Project)
            rich_print("Deleting documents...")
            documents = DocumentRepo.get_all(db)
            for document in documents:
                DocumentRepo.delete(db, document.id)
            rich_print(f"✓ Deleted {len(documents)} documents")

            # 11. Delete Projects (root entity)
            rich_print("Deleting projects...")
            projects = ProjectRepo.get_all(db)
            for project in projects:
                ProjectRepo.delete(db, project.id)
            rich_print(f"✓ Deleted {len(projects)} projects")

            # Commit all changes
            db.commit()

            # Verify deletion
            rich_print("\nVerifying deletion...")
            final_counts = get_table_counts(db)
            final_total = sum(count for _, count in final_counts)

            if final_total == 0:
                rich_print("✅ All data successfully deleted from the database!")
                rich_print("📊 Summary of deleted records:")
                for table_name, count in counts:
                    if count > 0:
                        rich_print(f"   • {table_name}: {count}")
            else:
                rich_print(f"⚠️  Warning: {final_total} records still remain in the database.")
                for table_name, count in final_counts:
                    if count > 0:
                        rich_print(f"   • {table_name}: {count}")

        except Exception as e:
            rich_print(f"❌ Error during data deletion: {e}")
            db.rollback()
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete all data from the database.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt and proceed with deletion.",
    )
    args = parser.parse_args()

    try:
        delete_all_data(force=args.force)
    except KeyboardInterrupt:
        rich_print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        rich_print(f"\nFatal error: {e}")
        sys.exit(1)
