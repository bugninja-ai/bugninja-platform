"""
Database base and model exports.

This module provides the base class and exports all database models.
"""

from sqlalchemy import create_engine  # , event
from sqlalchemy.orm import (
    DeclarativeMeta,
    configure_mappers,
    declarative_base,
    sessionmaker,
)

from app.config import settings

# Import all models to ensure they are registered
from app.db.action import Action
from app.db.brain_state import BrainState
from app.db.browser_config import BrowserConfig
from app.db.cost import Cost
from app.db.document import Document
from app.db.history_element import HistoryElement
from app.db.project import Project
from app.db.secret_value import SecretValue
from app.db.secret_value_test_traversal import SecretValueTestTraversal
from app.db.test_case import TestCase
from app.db.test_case_browser_config import TestCaseBrowserConfig
from app.db.test_run import TestRun

# from app.middleware.sqlcommenter import BeforeExecuteFactory

db_engine = create_engine(settings.DATABASE_URL, pool_size=50, max_overflow=50)
# TODO! re-enable for more robust logging regarding database actions, problems etc...
# listener = BeforeExecuteFactory(
#     with_db_driver=True,
#     with_db_framework=True,
#     # you may use one of opencensus or opentelemetry
#     with_opentelemetry=True,
# )
# event.listen(db_engine, "before_cursor_execute", listener, retval=True)

configure_mappers()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base: DeclarativeMeta = declarative_base()


class DBTableBaseModel(Base):  # type: ignore
    __abstract__ = True


DOCUMENT_ELEMENT = "document_element"
NOTE_ELEMENT = "note_element"


__all__ = [
    "Base",
    "Action",
    "BrainState",
    "BrowserConfig",
    "Cost",
    "Document",
    "HistoryElement",
    "Project",
    "SecretValue",
    "SecretValueTestTraversal",
    "TestCase",
    "TestCaseBrowserConfig",
    "TestRun",
    "TestRun",
]
