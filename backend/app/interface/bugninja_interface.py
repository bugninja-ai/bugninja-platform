"""
Bugninja Interface

This module provides an interface for reconstructing Bugninja traversal objects from database data.
It gathers all necessary information from the database to create Traversal objects for execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, TypedDict

from bugninja import BugninjaTask, Traversal  # type: ignore
from rich import print as rich_print
from sqlmodel import Session

from app.db.browser_config import BrowserConfig
from app.db.history_element import HistoryElementState
from app.db.test_case import TestCase
from app.db.test_run import RunOrigin, RunState, RunType
from app.repo.action_repo import ActionRepo
from app.repo.brain_state_repo import BrainStateRepo
from app.repo.browser_config_repo import BrowserConfigRepo
from app.repo.history_element_repo import HistoryElementRepo
from app.repo.secret_value_repo import SecretValueRepo
from app.repo.test_case_repo import TestCaseRepo
from app.repo.test_run_repo import TestRunRepo
from app.repo.test_traversal_repo import TestTraversalRepo
from app.schemas.communication.test_run import ExtendedResponseBrainState
from app.schemas.crud.action import CreateAction
from app.schemas.crud.brain_state import CreateBrainState
from app.schemas.crud.history_element import CreateHistoryElement
from app.schemas.crud.test_run import CreateTestRun


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
        # TODO!: it is not a criteria to be completed
        # # Validate traversal has completed runs
        # completed_traversal_ids = TestRunRepo.get_traversal_ids_with_completed_runs(
        #     db, [traversal_id]
        # )
        # if not completed_traversal_ids:
        #     raise ValueError(f"Traversal {traversal_id} has no completed test runs")

        # Get basic traversal data
        test_traversal = TestTraversalRepo.get_by_id(db, traversal_id)
        if not test_traversal:
            rich_print(f"Could not find test traversal with id: '{traversal_id}'")
            return None

        # Get test case data
        test_case = TestCaseRepo.get_by_id(db, test_traversal.test_case_id)
        if not test_case:
            rich_print(f"Could not find test case with id: '{test_traversal.test_case_id}'")
            return None

        # Get browser config data
        browser_config = BrowserConfigRepo.get_by_id(db, test_traversal.browser_config_id)
        if not browser_config:
            rich_print(f"Could not find test case with id: '{test_traversal.test_case_id}'")
            return None

        # Get brain states with actions
        repo_instance = TestRunRepo()
        extended_brain_states = repo_instance.get_extended_brain_states_by_test_traversal_id(
            db, traversal_id
        )

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

                # Ensure browser_config has the required field mapping for bugninja
        browser_config_data = browser_config.browser_config.copy()

        # Map browser_channel to channel if channel is missing but browser_channel exists
        if "channel" not in browser_config_data and "browser_channel" in browser_config_data:
            browser_config_data["channel"] = browser_config_data["browser_channel"]

        # Map frontend browser channel names to bugninja enum values
        if "channel" in browser_config_data:
            browser_config_data["channel"] = BugninjaInterface._map_browser_channel_to_enum(
                browser_config_data["channel"]
            )

        return {
            "test_case": test_case.test_description,
            "browser_config": browser_config_data,
            "secrets": secrets,
            "brain_states": brain_states_dict,
            "actions": actions_dict,
        }

    @staticmethod
    def _map_browser_channel_to_enum(channel: str) -> str:
        """
        Map frontend browser channel names to bugninja package enum values.

        Args:
            channel (str): Frontend browser channel name

        Returns:
            str: Bugninja package compatible enum value
        """
        # Mapping from frontend names to bugninja enum values
        channel_mapping = {
            "Chromium": "chromium",
            "Google Chrome": "chrome",
            "Microsoft Edge": "msedge",
            "Firefox": "firefox",  # Note: firefox might not be supported by bugninja
            "Webkit": "webkit",  # Note: webkit might not be supported by bugninja
            "Mobile Chrome": "chrome",
            "Mobile Safari": "webkit",
        }

        # Return mapped value or default to chromium if unknown
        return channel_mapping.get(channel, "chromium")

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

    @staticmethod
    def save_brain_state(
        db: Session,
        test_traversal_id: str,
        brain_state_data: Dict[str, Any],
        test_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save a new brain state and auto-create test run if needed.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier
            brain_state_data: Brain state data dictionary
            test_run_id: Optional test run ID (auto-created if not provided)

        Returns:
            Dict[str, Any]: Dictionary containing brain_state_id, test_run_id, idx_in_run, and success status

        Raises:
            ValueError: If brain state data is invalid
        """
        try:
            # Validate brain state data
            BugninjaInterface._validate_brain_state_data(brain_state_data)

            # Create test run if not provided
            if not test_run_id:
                test_run_id = BugninjaInterface._create_test_run(db, test_traversal_id)

            # Get next brain state index (only counting valid brain states)
            next_idx = BugninjaInterface._get_next_brain_state_index(db, test_traversal_id)

            # Create brain state using proper schema

            create_data = CreateBrainState(
                test_traversal_id=test_traversal_id,
                idx_in_run=next_idx,
                valid=True,
                evaluation_previous_goal=brain_state_data.get("evaluation_previous_goal", ""),
                memory=brain_state_data.get("memory", ""),
                next_goal=brain_state_data.get("next_goal", ""),
            )

            brain_state = BrainStateRepo.create(db, create_data)

            return {
                "brain_state_id": brain_state.id,
                "test_run_id": test_run_id,
                "idx_in_run": brain_state.idx_in_run,
                "success": True,
            }

        except Exception as e:
            return {
                "brain_state_id": None,
                "test_run_id": test_run_id,
                "idx_in_run": None,
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def save_action(
        db: Session, brain_state_id: str, action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save a new action for a specific brain state.

        Args:
            db: Database session
            brain_state_id: Brain state identifier
            action_data: Action data dictionary

        Returns:
            Dict[str, Any]: Dictionary containing action_id, idx_in_brain_state, and success status

        Raises:
            ValueError: If brain_state_id doesn't exist or action data is invalid
        """
        try:
            # Validate brain state exists

            brain_state = BrainStateRepo.get_by_id(db, brain_state_id)
            if not brain_state:
                raise ValueError(f"Brain state with id {brain_state_id} not found")

            # Validate action data
            BugninjaInterface._validate_action_data(action_data)

            # Get next action index (only counting valid actions)
            next_idx = BugninjaInterface._get_next_action_index(db, brain_state_id)

            # Create action using proper schema

            create_data = CreateAction(
                brain_state_id=brain_state_id,
                idx_in_brain_state=next_idx,
                valid=True,
                action=action_data.get("action", {}),
                dom_element_data=action_data.get("dom_element_data", {}),
            )

            action = ActionRepo.create(db, create_data)

            return {
                "action_id": action.id,
                "idx_in_brain_state": action.idx_in_brain_state,
                "success": True,
            }

        except Exception as e:
            return {
                "action_id": None,
                "idx_in_brain_state": None,
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def save_history_element(
        db: Session,
        action_id: str,
        history_element_data: Dict[str, Any],
        test_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save a history element for a specific action.

        Args:
            db: Database session
            action_id: Action identifier
            history_element_data: History element data dictionary
            test_run_id: Optional test run ID (required if not provided in history_element_data)

        Returns:
            Dict[str, Any]: Dictionary containing history_element_id, test_run_id, and success status

        Raises:
            ValueError: If action_id doesn't exist or history element data is invalid
        """
        try:
            # Validate action exists

            action = ActionRepo.get_by_id(db, action_id)
            if not action:
                raise ValueError(f"Action with id {action_id} not found")

            # Get test_run_id from action's brain state if not provided
            if not test_run_id:

                brain_state = BrainStateRepo.get_by_id(db, action.brain_state_id)
                if not brain_state:
                    raise ValueError(f"Brain state for action {action_id} not found")

                # Get test run for this traversal

                test_run = TestRunRepo.get_latest_by_test_traversal(
                    db, brain_state.test_traversal_id
                )
                if not test_run:
                    raise ValueError(
                        f"No test run found for traversal {brain_state.test_traversal_id}"
                    )

                test_run_id = test_run.id

            # Validate history element data
            BugninjaInterface._validate_history_element_data(history_element_data)

            # Create history element using proper schema

            create_data = CreateHistoryElement(
                test_run_id=test_run_id,
                action_id=action_id,
                history_element_state=HistoryElementState(
                    history_element_data.get("history_element_state", "PASSED")
                ),
                screenshot=history_element_data.get("screenshot", ""),
                action_finished_at=datetime.now(),
            )

            history_element = HistoryElementRepo.create(db, create_data)

            return {
                "history_element_id": history_element.id,
                "test_run_id": test_run_id,
                "success": True,
            }

        except Exception as e:
            return {
                "history_element_id": None,
                "test_run_id": test_run_id,
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def invalidate_traversal_data(db: Session, test_traversal_id: str) -> Dict[str, Any]:
        """
        Set all brain states and actions for traversal to valid = False.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            Dict[str, Any]: Dictionary containing counts of invalidated items and success status
        """
        try:
            # Invalidate brain states

            brain_states = BrainStateRepo.get_by_test_traversal_id(db, test_traversal_id)
            invalidated_brain_states = 0

            for brain_state in brain_states:
                if brain_state.valid:
                    brain_state.valid = False
                    db.add(brain_state)
                    invalidated_brain_states += 1

            # Invalidate actions

            invalidated_actions = 0
            for brain_state in brain_states:
                actions = ActionRepo.get_by_brain_state_id(db, brain_state.id)
                for action in actions:
                    if action.valid:
                        action.valid = False
                        db.add(action)
                        invalidated_actions += 1

            db.commit()

            return {
                "invalidated_brain_states": invalidated_brain_states,
                "invalidated_actions": invalidated_actions,
                "success": True,
            }

        except Exception as e:
            db.rollback()
            return {
                "invalidated_brain_states": 0,
                "invalidated_actions": 0,
                "success": False,
                "error": str(e),
            }

    # Helper methods

    @staticmethod
    def _create_test_run(db: Session, test_traversal_id: str) -> str:
        """
        Create a new test run for the given traversal.

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            str: Created test run ID
        """

        # Get traversal to get browser config ID
        test_traversal = TestTraversalRepo.get_by_id(db, test_traversal_id)
        if not test_traversal:
            raise ValueError(f"Test traversal with id {test_traversal_id} not found")

        create_data = CreateTestRun(
            test_traversal_id=test_traversal_id,
            browser_config_id=test_traversal.browser_config_id,
            run_type=RunType.AGENTIC,
            origin=RunOrigin.USER,
            repair_was_needed=False,
            current_state=RunState.PENDING,
            run_gif="",
        )

        test_run = TestRunRepo.create(db, create_data)
        return test_run.id

    @staticmethod
    def _get_next_brain_state_index(db: Session, test_traversal_id: str) -> int:
        """
        Get the next brain state index (only counting valid brain states).

        Args:
            db: Database session
            test_traversal_id: Test traversal identifier

        Returns:
            int: Next index (0 if no valid brain states exist)
        """

        brain_states = BrainStateRepo.get_by_test_traversal_id(db, test_traversal_id)
        valid_brain_states = [bs for bs in brain_states if bs.valid]

        if not valid_brain_states:
            return 0

        max_idx = max(bs.idx_in_run for bs in valid_brain_states)
        return max_idx + 1

    @staticmethod
    def _get_next_action_index(db: Session, brain_state_id: str) -> int:
        """
        Get the next action index (only counting valid actions).

        Args:
            db: Database session
            brain_state_id: Brain state identifier

        Returns:
            int: Next index (0 if no valid actions exist)
        """

        actions = ActionRepo.get_by_brain_state_id(db, brain_state_id)
        valid_actions = [action for action in actions if action.valid]

        if not valid_actions:
            return 0

        max_idx = max(action.idx_in_brain_state for action in valid_actions)
        return max_idx + 1

    @staticmethod
    def _validate_brain_state_data(brain_state_data: Dict[str, Any]) -> None:
        """
        Validate brain state data.

        Args:
            brain_state_data: Brain state data dictionary

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(brain_state_data, dict):
            raise ValueError("Brain state data must be a dictionary")

        required_fields = ["evaluation_previous_goal", "memory", "next_goal"]
        for field in required_fields:
            if field not in brain_state_data:
                raise ValueError(f"Missing required field: {field}")

    @staticmethod
    def _validate_action_data(action_data: Dict[str, Any]) -> None:
        """
        Validate action data.

        Args:
            action_data: Action data dictionary

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(action_data, dict):
            raise ValueError("Action data must be a dictionary")

        if "action" not in action_data:
            raise ValueError("Missing required field: action")

    @staticmethod
    def _validate_history_element_data(history_element_data: Dict[str, Any]) -> None:
        """
        Validate history element data.

        Args:
            history_element_data: History element data dictionary

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(history_element_data, dict):
            raise ValueError("History element data must be a dictionary")

        # history_element_state is optional, defaults to PASSED
        # screenshot is optional
