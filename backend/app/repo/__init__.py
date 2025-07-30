"""
Repository Package

This package contains repository classes for database CRUD operations.
All repositories use static methods and require a database session to be provided.
"""

from .action_repo import ActionRepo
from .brain_state_repo import BrainStateRepo
from .browser_config_repo import BrowserConfigRepo
from .cost_repo import CostRepo
from .document_repo import DocumentRepo
from .history_element_repo import HistoryElementRepo
from .project_repo import ProjectRepo
from .secret_value_repo import SecretValueRepo
from .test_case_repo import TestCaseRepo
from .test_run_repo import TestRunRepo
from .test_traversal_repo import TestTraversalRepo

# Communication schemas for extended responses
from app.schemas.communication.project import (
    ExtendedResponseProject,
    LightResponseTestcase,
    ResponseSecretsOfProject,
)
from app.schemas.communication.test_case import ExtendedResponseTestcase
from app.schemas.communication.test_traversal import (
    ExtendedResponseTestTraversal,
    LightResponseTestRun,
)

__all__ = [
    # Core entity repositories
    "ProjectRepo",
    "DocumentRepo",
    "TestCaseRepo",
    "SecretValueRepo",
    "BrowserConfigRepo",
    "TestTraversalRepo",
    "TestRunRepo",
    # Execution-related repositories
    "ActionRepo",
    "BrainStateRepo",
    "HistoryElementRepo",
    "CostRepo",
    # Communication schemas for extended responses
    "ExtendedResponseProject",
    "LightResponseTestcase",
    "ResponseSecretsOfProject",
    "ExtendedResponseTestcase",
    "ExtendedResponseTestTraversal",
    "LightResponseTestRun",
]
