from datetime import datetime
from typing import Any, Dict, Optional

from browser_use.agent.views import AgentBrain  # type: ignore
from bugninja.events import EventPublisher  # type: ignore
from bugninja.schemas.pipeline import BugninjaExtendedAction  # type: ignore
from rich import print as rich_print
from sqlmodel import Session

from app.db.action import Action
from app.db.base import QuinoContextManager
from app.db.brain_state import BrainState
from app.db.history_element import HistoryElement, HistoryElementState
from app.db.test_run import RunState
from app.repo.action_repo import ActionRepo
from app.repo.brain_state_repo import BrainStateRepo
from app.repo.history_element_repo import HistoryElementRepo
from app.repo.test_run_repo import TestRunRepo
from app.schemas.crud.action import CreateAction
from app.schemas.crud.brain_state import CreateBrainState
from app.schemas.crud.history_element import CreateHistoryElement
from app.schemas.crud.test_run import UpdateTestRun


class DBWriteEventPublisher(EventPublisher):
    """Database write event publisher for Bugninja actions."""

    def is_available(self) -> bool:
        return True

    async def initialize_run(
        self, run_type: str, metadata: Dict[str, Any], existing_run_id: Optional[str] = None
    ) -> str:
        return ""

    async def update_run_state(self, run_id: str, state: RunState) -> None: ...  # type:ignore

    async def complete_run(self, run_id: str, success: bool, error: Optional[str] = None) -> None:

        rich_print(f"Run '{run_id}' completed!")
        rich_print(f"Success: {success}")
        rich_print(f"Error: {error}")

        update = UpdateTestRun(
            repair_was_needed=False,
            finished_at=datetime.now(),
            current_state=RunState.FAILED if not success or error else RunState.FINISHED,
            run_gif=None,
        )

        with QuinoContextManager() as db:
            TestRunRepo.update(
                db=db,
                test_run_id=run_id,
                test_run_data=update,
            )

    async def publish_action_event(
        self,
        run_id: str,
        brain_state_id: str,
        actual_brain_state: AgentBrain,
        action_result_data: BugninjaExtendedAction,
    ) -> None:
        """
        Publish action event to database.

        Creates or retrieves brain state, creates action, and creates history element
        for each action event from Bugninja.

        Args:
            run_id: Test run identifier
            brain_state_id: Brain state identifier
            actual_brain_state: Current brain state data
            action_result_data: Action execution results
        """
        with QuinoContextManager() as db:
            # Validate test run exists
            test_run = TestRunRepo.get_by_id(db, run_id)
            if not test_run:
                raise ValueError(f"Test run with ID: '{run_id}' not found")

            # Get or create brain state
            brain_state = self._get_or_create_brain_state(
                db, brain_state_id, actual_brain_state, test_run.test_traversal_id
            )

            # Create action
            action: Action = self._create_action(db, brain_state.id, action_result_data)

            # Create history element
            history_element = self._create_history_element(
                db, run_id, action.id, action_result_data
            )

            rich_print(
                f"DB WRITE EVENT COMPLETED: {run_id} -> {brain_state_id} -> {action.id} -> {history_element.id}"
            )

    def _get_or_create_brain_state(
        self,
        db: Session,
        brain_state_id: str,
        actual_brain_state: AgentBrain,
        test_traversal_id: str,
    ) -> BrainState:
        """
        Get existing brain state or create new one.

        Args:
            db: Database session
            brain_state_id: Brain state identifier
            actual_brain_state: Brain state data
            test_traversal_id: Test traversal identifier

        Returns:
            BrainState: Existing or newly created brain state
        """
        # Check if brain state already exists
        existing_brain_state = BrainStateRepo.get_by_id(db, brain_state_id)

        if existing_brain_state:
            # Brain state exists, return it
            return existing_brain_state

        # Create new brain state
        brain_state_data = CreateBrainState(
            test_traversal_id=test_traversal_id,
            idx_in_run=BrainStateRepo.get_number_of_brainstates_for_test_traversal(
                db, test_traversal_id
            )
            + 1,
            valid=True,
            evaluation_previous_goal=actual_brain_state.evaluation_previous_goal,
            memory=actual_brain_state.memory,
            next_goal=actual_brain_state.next_goal,
        )

        # Override the generated ID with the provided brain_state_id
        brain_state = BrainStateRepo.create(db, brain_state_data)

        # Update the ID to match the provided brain_state_id
        brain_state.id = brain_state_id
        db.add(brain_state)
        db.commit()
        db.refresh(brain_state)

        return brain_state

    def _create_action(
        self, db: Session, brain_state_id: str, action_result_data: BugninjaExtendedAction
    ) -> Action:
        """
        Create new action record.

        Args:
            db: Database session
            brain_state_id: Brain state identifier
            action_result_data: Action execution data

        Returns:
            Action: Created action record
        """

        dom_element_data: Dict[str, Any] = action_result_data.dom_element_data or {}

        action_data = CreateAction(
            brain_state_id=brain_state_id,
            idx_in_brain_state=action_result_data.idx_in_brainstate,
            action=action_result_data.action,
            dom_element_data=dom_element_data,
            valid=True,
        )

        return ActionRepo.create(db, action_data)

    def _create_history_element(
        self,
        db: Session,
        test_run_id: str,
        action_id: str,
        action_result_data: BugninjaExtendedAction,
    ) -> HistoryElement:
        """
        Create new history element record.

        Args:
            db: Database session
            test_run_id: Test run identifier
            action_id: Action identifier
            action_result_data: Action execution data

        Returns:
            HistoryElement: Created history element record
        """

        history_element_data = CreateHistoryElement(
            test_run_id=test_run_id,
            action_id=action_id,
            history_element_state=HistoryElementState.PASSED,
            screenshot=action_result_data.screenshot_filename or "",
            action_finished_at=datetime.now(),
        )

        return HistoryElementRepo.create(db, history_element_data)
