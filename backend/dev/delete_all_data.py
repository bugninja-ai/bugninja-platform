"""
Delete All Data Script

This script deletes all data from the database across all tables.
Use this script to clear the database before uploading mock data.

⚠️  WARNING: This will permanently delete ALL data from the database!
"""

import argparse
import os
import shutil
import sys

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


def cleanup_content_folder() -> None:
    """
    Clean up the content folder by removing all files and subdirectories.

    This function removes:
    - content/run_gifs/ (and all files within)
    - content/run_he_screenshots/ (and all files within)
    - content/ (if empty after cleanup)
    """
    content_dir = "content"

    if not os.path.exists(content_dir):
        rich_print("✓ Content folder does not exist, nothing to clean up.")
        return

    rich_print("🗑️  Cleaning up content folder...")

    # Clean up run_gifs directory
    run_gifs_dir = os.path.join(content_dir, "run_gifs")
    if os.path.exists(run_gifs_dir):
        try:
            shutil.rmtree(run_gifs_dir)
            rich_print(f"✓ Deleted directory: {run_gifs_dir}")
        except Exception as e:
            rich_print(f"❌ Error deleting {run_gifs_dir}: {e}")

    # Clean up run_he_screenshots directory
    run_he_screenshots_dir = os.path.join(content_dir, "run_he_screenshots")
    if os.path.exists(run_he_screenshots_dir):
        try:
            shutil.rmtree(run_he_screenshots_dir)
            rich_print(f"✓ Deleted directory: {run_he_screenshots_dir}")
        except Exception as e:
            rich_print(f"❌ Error deleting {run_he_screenshots_dir}: {e}")

    # Remove content directory if it's empty
    try:
        if os.path.exists(content_dir) and not os.listdir(content_dir):
            os.rmdir(content_dir)
            rich_print(f"✓ Deleted empty directory: {content_dir}")
        elif os.path.exists(content_dir):
            rich_print(f"✓ Content directory {content_dir} still exists (not empty)")
    except Exception as e:
        rich_print(f"❌ Error removing content directory: {e}")

    rich_print("✅ Content folder cleanup completed!")


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


def delete_all_data(force: bool = False) -> None:
    """
    Delete all data from the database across all tables.

    This function deletes data in the correct order to respect foreign key constraints.
    """
    with QuinoContextManager() as db:
        try:
            rich_print("Checking current database state...")

            # Get current counts
            # Ask for confirmation
            if not confirm_deletion(force=force):
                rich_print("Operation cancelled.")
                return

            rich_print("🗑️  Starting data deletion...")

            # Delete in order to respect foreign key constraints
            # Start with entities that have no dependencies

            # 1. Delete History Elements (depends on TestRun and Action)
            rich_print("Deleting history elements...")
            HistoryElementRepo.delete_all(db)
            rich_print("✓ Deleted history elements")

            # 2. Delete Costs (depends on TestRun and Project)
            rich_print("Deleting costs...")
            CostRepo.delete_all(db)
            rich_print("✓ Deleted costs")

            # 3. Delete Actions (depends on BrainState)
            rich_print("Deleting actions...")
            ActionRepo.delete_all(db)
            rich_print("✓ Deleted all actions")

            # 4. Delete Brain States (depends on TestTraversal)
            rich_print("Deleting brain states...")
            BrainStateRepo.delete_all(db)
            rich_print("✓ Deleted brain states")

            # 5. Delete Test Runs (depends on TestTraversal and BrowserConfig)
            rich_print("Deleting test runs...")
            TestRunRepo.delete_all(db)
            rich_print("✓ Deleted test runs")

            # 6. Delete Test Traversals (depends on TestCase and BrowserConfig)
            rich_print("Deleting test traversals...")
            TestTraversalRepo.delete_all(db)
            rich_print("✓ Deleted test traversals")

            # 6.5. Delete Association Tables (must be deleted before main entities)
            rich_print("Deleting association table entries...")

            # Delete TestCaseBrowserConfig associations using direct SQL
            result = db.exec(text("DELETE FROM testcasebrowserconfig"))
            rich_print(f"✓ Deleted {result.rowcount} test case - browser config associations")

            # Delete SecretValueTestCase associations using direct SQL
            result = db.exec(text("DELETE FROM secretvaluetestcase"))
            rich_print(f"✓ Deleted {result.rowcount} secret value - test case associations")

            # 7. Delete Test Cases (depends on Project and Document)
            rich_print("Deleting test cases...")
            TestCaseRepo.delete_all(db)
            rich_print("✓ Deleted test cases")

            # 8. Delete Browser Configs (depends on Project)
            rich_print("Deleting browser configs...")
            BrowserConfigRepo.delete_all(db)
            rich_print("✓ Deleted browser configs")

            # 9. Delete Secret Values (depends on Project)
            rich_print("Deleting secret values...")
            SecretValueRepo.delete_all(db)
            rich_print("✓ Deleted secret values")

            # 10. Delete Documents (depends on Project)
            rich_print("Deleting documents...")
            DocumentRepo.delete_all(db)
            rich_print("✓ Deleted documents")

            # 11. Delete Projects (root entity)
            rich_print("Deleting projects...")
            ProjectRepo.delete_all(db)
            rich_print("✓ Deleted projects")

            # Commit all changes
            db.commit()

            # Clean up content folder
            cleanup_content_folder()

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
