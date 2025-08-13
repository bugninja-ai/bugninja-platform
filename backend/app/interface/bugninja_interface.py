"""
Bugninja Interface

This module provides an interface for reconstructing Bugninja traversal objects from database data.
It gathers all necessary information from the database to create Traversal objects for execution.
"""

from typing import Any, Dict, List, Optional, Set, TypedDict

from bugninja import BugninjaTask, Traversal  # type: ignore
from sqlmodel import Session

from app.db.browser_config import BrowserConfig
from app.db.test_case import TestCase
from app.repo.browser_config_repo import BrowserConfigRepo
from app.repo.secret_value_repo import SecretValueRepo
from app.repo.test_case_repo import TestCaseRepo
from app.repo.test_run_repo import TestRunRepo
from app.repo.test_traversal_repo import TestTraversalRepo
from app.schemas.communication.test_run import ExtendedResponseBrainState


class ProcessingContext(TypedDict):
    """Type definition for processing context."""

    traversal_data: Dict[str, Dict[str, Any]]
    secrets_by_test_case: Dict[str, List[Any]]  # SecretValue objects
    brain_states_by_traversal: Dict[str, List[ExtendedResponseBrainState]]
    completed_traversal_ids: Set[str]


class BugninjaInterface:
    """
    Interface for reconstructing Bugninja traversal objects from database data.

    Provides methods to gather all necessary data for traversal execution.
    """

    @staticmethod
    def get_traversal_data(db: Session, traversal_id: str) -> Optional[Traversal]:
        """
        Retrieve complete traversal data for Bugninja execution.

        Args:
            db: Database session
            traversal_id: Test traversal identifier

        Returns:
            Optional[Traversal]: Bugninja Traversal object, or None if traversal not found

        Raises:
            ValueError: If traversal has no completed test runs
        """
        # Validate traversal has completed runs
        completed_traversal_ids = TestRunRepo.get_traversal_ids_with_completed_runs(
            db, [traversal_id]
        )
        if not completed_traversal_ids:
            raise ValueError(f"Traversal {traversal_id} has no completed test runs")

        # Get basic traversal data
        test_traversal = TestTraversalRepo.get_by_id(db, traversal_id)
        if not test_traversal:
            return None

        # Get test case data
        test_case = TestCaseRepo.get_by_id(db, test_traversal.test_case_id)
        if not test_case:
            return None

        # Get browser config data
        browser_config = BrowserConfigRepo.get_by_id(db, test_traversal.browser_config_id)
        if not browser_config:
            return None

        # Get brain states with actions
        repo_instance = TestRunRepo()
        extended_brain_states = repo_instance.get_extended_brain_states_by_test_traversal_id(
            db, traversal_id
        )
        if not extended_brain_states:
            return None

        # Get secrets by test case ID
        secret_values = SecretValueRepo.get_by_test_case_id(db, test_case.id)
        secrets = {secret.secret_name: secret.secret_value for secret in secret_values}

        # Transform data into Traversal format
        traversal_data = BugninjaInterface._build_traversal_data(
            test_case=test_case,
            browser_config=browser_config,
            brain_states=extended_brain_states,
            secrets=secrets,
        )

        return Traversal.model_validate(traversal_data)

    @staticmethod
    def get_task_data(db: Session, traversal_id: str) -> Optional[BugninjaTask]:
        """
        Retrieve task data for Bugninja initial run execution.

        Args:
            db: Database session
            traversal_id: Test traversal identifier

        Returns:
            Optional[BugninjaTask]: Bugninja Task object, or None if traversal not found
        """
        # Get basic traversal data
        test_traversal = TestTraversalRepo.get_by_id(db, traversal_id)
        if not test_traversal:
            return None

        # Get test case data
        test_case = TestCaseRepo.get_by_id(db, test_traversal.test_case_id)
        if not test_case:
            return None

        # Get browser config data
        browser_config = BrowserConfigRepo.get_by_id(db, test_traversal.browser_config_id)
        if not browser_config:
            return None

        # Get secrets by test case ID
        secret_values = SecretValueRepo.get_by_test_case_id(db, test_case.id)
        secrets = {secret.secret_name: secret.secret_value for secret in secret_values}

        # Transform data into Task format
        task_data = BugninjaInterface._build_task_data(
            test_case=test_case,
            browser_config=browser_config,
            secrets=secrets,
        )

        return BugninjaTask.model_validate(task_data)

    @staticmethod
    def get_multiple_traversal_data(
        db: Session, traversal_ids: List[str]
    ) -> Dict[str, Optional[Traversal]]:
        """
        Retrieve traversal data for multiple traversals efficiently.

        Args:
            db: Database session
            traversal_ids: List of test traversal identifiers

        Returns:
            Dict[str, Optional[Traversal]]: Dictionary mapping traversal_id to Traversal object or None
        """
        if not traversal_ids:
            return {}

        # Validate which traversals have completed runs
        completed_traversal_ids = TestRunRepo.get_traversal_ids_with_completed_runs(
            db, traversal_ids
        )
        completed_traversal_set: Set[str] = set(completed_traversal_ids)

        # Get all traversal data with related entities in a single query
        traversal_data: Dict[str, Dict[str, Any]] = TestTraversalRepo.get_by_ids_with_related_data(
            db, traversal_ids
        )

        # Get all secrets for all test cases in a single query
        test_case_ids = (
            data["test_case"].id for data in traversal_data.values() if data.get("test_case")
        )
        secrets_by_test_case = SecretValueRepo.get_by_test_case_ids(db, list(test_case_ids))

        # Get brain states for all traversals that have completed runs in a single query
        brain_states_by_traversal = TestRunRepo.get_extended_brain_states_by_traversal_ids(
            db, list(completed_traversal_set)
        )

        # Process all traversals in a single pass
        results: Dict[str, Optional[Traversal]] = {}
        for traversal_id in traversal_ids:
            if traversal_id not in traversal_data:
                results[traversal_id] = None
                continue

            data = traversal_data[traversal_id]
            test_case: TestCase = data["test_case"]
            browser_config: BrowserConfig = data["browser_config"]

            # Check if traversal has completed runs
            if traversal_id not in completed_traversal_set:
                results[traversal_id] = None
                continue

            # Get brain states for this traversal
            brain_states = brain_states_by_traversal.get(traversal_id, [])
            if not brain_states:
                results[traversal_id] = None
                continue

            # Get secrets for this test case
            secrets = secrets_by_test_case.get(test_case.id, [])
            secrets_dict = {secret.secret_name: secret.secret_value for secret in secrets}

            # Build traversal data
            try:
                traversal_data_dict = BugninjaInterface._build_traversal_data(
                    test_case=test_case,
                    browser_config=browser_config,
                    brain_states=brain_states,
                    secrets=secrets_dict,
                )
                results[traversal_id] = Traversal.model_validate(traversal_data_dict)
            except Exception:
                results[traversal_id] = None

        return results

    @staticmethod
    def get_multiple_task_data(
        db: Session, traversal_ids: List[str]
    ) -> Dict[str, Optional[BugninjaTask]]:
        """
        Retrieve task data for multiple traversals efficiently.

        Args:
            db: Database session
            traversal_ids: List of test traversal identifiers

        Returns:
            Dict[str, Optional[BugninjaTask]]: Dictionary mapping traversal_id to BugninjaTask object or None
        """
        if not traversal_ids:
            return {}

        # Get all traversal data with related entities in a single query
        traversal_data: Dict[str, Dict[str, Any]] = TestTraversalRepo.get_by_ids_with_related_data(
            db, traversal_ids
        )

        # Get all secrets for all test cases in a single query
        test_case_ids = (
            data["test_case"].id for data in traversal_data.values() if data.get("test_case")
        )
        secrets_by_test_case = SecretValueRepo.get_by_test_case_ids(db, list(test_case_ids))

        # Process all traversals in a single pass
        results: Dict[str, Optional[BugninjaTask]] = {}
        for traversal_id in traversal_ids:
            if traversal_id not in traversal_data:
                results[traversal_id] = None
                continue

            data = traversal_data[traversal_id]
            test_case: TestCase = data["test_case"]
            browser_config: BrowserConfig = data["browser_config"]

            # Get secrets for this test case
            secrets = secrets_by_test_case.get(test_case.id, [])
            secrets_dict = {secret.secret_name: secret.secret_value for secret in secrets}

            # Build task data
            try:
                task_data = BugninjaInterface._build_task_data(
                    test_case=test_case,
                    browser_config=browser_config,
                    secrets=secrets_dict,
                )
                results[traversal_id] = BugninjaTask.model_validate(task_data)
            except Exception:
                results[traversal_id] = None

        return results

    @staticmethod
    def _build_traversal_data(
        test_case: TestCase,
        browser_config: BrowserConfig,
        brain_states: List[ExtendedResponseBrainState],
        secrets: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Build traversal data dictionary from database objects.

        Args:
            test_case: TestCase database object
            browser_config: BrowserConfig database object
            brain_states: List of extended brain states
            secrets: Dictionary of secret key-value pairs

        Returns:
            Dict[str, Any]: Traversal data ready for Traversal object creation
        """
        # Build brain states dictionary
        brain_states_dict: Dict[str, Dict[str, str]] = {}
        actions_dict: Dict[str, Dict[str, Any]] = {}
        action_counter = 0

        for brain_state in brain_states:
            brain_state_id = brain_state.id

            # Add brain state
            brain_states_dict[brain_state_id] = {
                "evaluation_previous_goal": brain_state.evaluation_previous_goal,
                "memory": brain_state.memory,
                "next_goal": brain_state.next_goal,
            }

            # Add actions for this brain state
            for history_element in brain_state.history_elements:
                action_key = f"action_{action_counter}"
                actions_dict[action_key] = {
                    "brain_state_id": brain_state_id,
                    "action": history_element.action,
                    "dom_element_data": history_element.dom_element_data,
                    "screenshot_filename": history_element.screenshot,
                }
                action_counter += 1

        return {
            "test_case": test_case.test_goal,
            "browser_config": browser_config.browser_config,
            "secrets": secrets,
            "brain_states": brain_states_dict,
            "actions": actions_dict,
        }

    @staticmethod
    def _build_task_data(
        test_case: TestCase,
        browser_config: BrowserConfig,
        secrets: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Build task data dictionary from database objects.

        Args:
            test_case: TestCase database object
            browser_config: BrowserConfig database object
            secrets: Dictionary of secret key-value pairs

        Returns:
            Dict[str, Any]: Task data ready for BugninjaTask object creation
        """
        return {
            "test_case": test_case.test_goal,
            "url_route": test_case.url_route,
            "allowed_domains": test_case.allowed_domains,
            "extra_rules": test_case.extra_rules,
            "browser_config": browser_config.browser_config,
            "secrets": secrets,
        }
