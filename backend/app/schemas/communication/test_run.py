"""
Test run communication schemas.

This module defines the communication schemas for test run operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.schemas.crud.browser_config import ResponseBrowserConfig


class ResponseTestRun(BaseModel):
    """Response schema for test run."""

    id: str
    test_traversal_id: str
    browser_config_id: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    total_cost: float
    total_tokens: int
    screenshot: Optional[str]

    class Config:
        """Pydantic config."""

        from_attributes = True


class ExtendedResponseHistoryElement(BaseModel):
    """Extended response schema for history element with action data."""

    # History element fields
    id: str
    test_run_id: str
    action_id: str
    action_started_at: datetime
    action_finished_at: Optional[datetime]
    history_element_state: str
    screenshot: Optional[str]

    # Related action fields
    action: Dict[str, Any]
    dom_element_data: Dict[str, Any]
    valid: bool
    idx_in_brain_state: int

    class Config:
        """Pydantic config."""

        from_attributes = True

    @classmethod
    def sample_factory_build(
        cls,
        test_run_id: str,
        action_id: str,
    ) -> "ExtendedResponseHistoryElement":
        """Build a sample extended response history element."""
        from datetime import datetime, timezone

        from cuid2 import Cuid as CUID

        return cls(
            id=CUID().generate(),
            test_run_id=test_run_id,
            action_id=action_id,
            action_started_at=datetime.now(timezone.utc),
            action_finished_at=datetime.now(timezone.utc),
            history_element_state="PASSED",
            screenshot="sample_screenshot.png",
            action={"type": "click", "selector": "#button", "text": "Click me"},
            dom_element_data={"tag": "button", "id": "button", "text": "Click me"},
            valid=True,
            idx_in_brain_state=0,
        )


class ExtendedResponseBrainState(BaseModel):
    """Extended response schema for brain state with history elements."""

    id: str
    test_traversal_id: str
    idx_in_run: int
    valid: bool
    evaluation_previous_goal: str
    memory: str
    next_goal: str
    history_elements: List[ExtendedResponseHistoryElement]

    class Config:
        """Pydantic config."""

        from_attributes = True

    @classmethod
    def sample_factory_build(
        cls,
        test_traversal_id: str,
        history_element_count: int = 2,
    ) -> "ExtendedResponseBrainState":
        """Build a sample extended response brain state."""
        from cuid2 import Cuid as CUID

        history_elements = []
        if history_element_count > 0:
            history_elements = [
                ExtendedResponseHistoryElement.sample_factory_build(
                    test_run_id=CUID().generate(),
                    action_id=CUID().generate(),
                )
                for _ in range(history_element_count)
            ]

        return cls(
            id=CUID().generate(),
            test_traversal_id=test_traversal_id,
            idx_in_run=0,
            valid=True,
            evaluation_previous_goal="Previous goal was achieved successfully",
            memory="Current context and state information",
            next_goal="Proceed to the next step in the test",
            history_elements=history_elements,
        )


class ExtendedResponseTestRun(BaseModel):
    """Extended response schema for test run with brain states and test case information."""

    id: str
    test_traversal_id: str
    browser_config_id: Optional[str]
    run_type: str
    origin: str
    repair_was_needed: bool
    current_state: str
    started_at: datetime
    finished_at: Optional[datetime]
    run_gif: str
    browser_config: Optional[ResponseBrowserConfig]
    test_case: Optional[Dict[str, Any]]  # Using Dict to avoid circular import
    brain_states: List[ExtendedResponseBrainState]
    passed_steps: int
    failed_steps: int
    total_steps: int

    class Config:
        """Pydantic config."""

        from_attributes = True

    @classmethod
    def sample_factory_build(
        cls,
        test_traversal_id: str,
        project_id: str,
        include_brain_states: bool = True,
        brain_state_count: int = 3,
    ) -> "ExtendedResponseTestRun":
        """Build a sample extended response test run."""
        from datetime import datetime, timezone

        from cuid2 import Cuid as CUID

        brain_states = []
        if include_brain_states:
            brain_states = [
                ExtendedResponseBrainState.sample_factory_build(
                    test_traversal_id=test_traversal_id,
                    history_element_count=2,
                )
                for _ in range(brain_state_count)
            ]

        return cls(
            id=CUID().generate(),
            test_traversal_id=test_traversal_id,
            browser_config_id=CUID().generate(),
            run_type="AGENTIC",
            origin="USER",
            repair_was_needed=False,
            current_state="FINISHED",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            run_gif="sample_run.gif",
            browser_config=ResponseBrowserConfig.sample_factory_build(),
            test_case=None,  # Will be populated with real test case data
            brain_states=brain_states,
            passed_steps=5,
            failed_steps=1,
            total_steps=6,
        )


class PaginatedResponseExtendedTestRun(BaseModel):
    """Paginated response schema for extended test runs."""

    items: List[ExtendedResponseTestRun]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    class Config:
        """Pydantic config."""

        from_attributes = True

    @classmethod
    def sample_factory_build(
        cls,
        test_traversal_id: str,
        project_id: str,
        include_brain_states: bool = True,
        brain_state_count: int = 3,
        items_in_page: int = 5,
        total_items: int = 25,
        page: int = 1,
        page_size: int = 10,
    ) -> "PaginatedResponseExtendedTestRun":
        """Build a sample paginated response for extended test runs."""
        from cuid2 import Cuid as CUID

        # Generate sample extended test run items
        extended_test_run_items = [
            ExtendedResponseTestRun.sample_factory_build(
                test_traversal_id=test_traversal_id or CUID().generate(),
                project_id=project_id,
                include_brain_states=include_brain_states,
                brain_state_count=brain_state_count,
            )
            for _ in range(items_in_page)
        ]

        total_pages = (total_items + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            items=extended_test_run_items,
            total_count=total_items,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )
