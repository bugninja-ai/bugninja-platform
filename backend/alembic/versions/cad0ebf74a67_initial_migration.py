"""initial_migration

Revision ID: cad0ebf74a67
Revises:
Create Date: 2025-07-20 16:42:30.374490

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel.sql.sqltypes import AutoString

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cad0ebf74a67"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum types
    runtype_enum = postgresql.ENUM(
        "AGENTIC",
        "REPLAY",
        "REPLAY_WITH_HEALING",
        name="runtype",
        create_type=False,
    )

    runorigin_enum = postgresql.ENUM(
        "USER",
        "CICD",
        name="runorigin",
        create_type=False,
    )

    runstate_enum = postgresql.ENUM(
        "STARTING",
        "RUNNING",
        "FINISHED",
        name="runstate",
        create_type=False,
    )

    historyelementstate_enum = postgresql.ENUM(
        "PASSED",
        "FAILED",
        name="historyelementstate",
        create_type=False,
    )

    bind = op.get_bind()

    # Create enums with checkfirst=True
    runtype_enum.create(bind, checkfirst=True)
    runorigin_enum.create(bind, checkfirst=True)
    runstate_enum.create(bind, checkfirst=True)
    historyelementstate_enum.create(bind, checkfirst=True)

    op.create_table(
        "project",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "name",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "default_start_url",
            AutoString(length=500),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "browserconfig",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "project_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("browser_config", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "document",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "project_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "name",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("content", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "secretvalue",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "project_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "secret_name",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("secret_value", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "testcase",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "project_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "test_name",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "test_description",
            AutoString(),
            nullable=False,
        ),
        sa.Column("test_goal", AutoString(), nullable=False),
        sa.Column("extra_rules", AutoString(), nullable=False),
        sa.Column(
            "url_route",
            AutoString(length=500),
            nullable=False,
        ),
        sa.Column("allowed_domains", postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["document.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "testcasebrowserconfig",
        sa.Column(
            "test_case_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "browser_config_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["browser_config_id"],
            ["browserconfig.id"],
        ),
        sa.ForeignKeyConstraint(
            ["test_case_id"],
            ["testcase.id"],
        ),
        sa.PrimaryKeyConstraint("test_case_id", "browser_config_id"),
    )
    op.create_table(
        "testtraversal",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "test_case_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "browser_config_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "traversal_name",
            AutoString(length=255),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["browser_config_id"], ["browserconfig.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_case_id"], ["testcase.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "brainstate",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "test_traversal_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("idx_in_run", sa.Integer(), nullable=False),
        sa.Column("valid", sa.Boolean(), nullable=False),
        sa.Column(
            "evaluation_previous_goal",
            AutoString(),
            nullable=False,
        ),
        sa.Column("memory", AutoString(), nullable=False),
        sa.Column("next_goal", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["test_traversal_id"], ["testtraversal.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "secretvaluetesttraversal",
        sa.Column(
            "secret_value_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "test_traversal_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["secret_value_id"],
            ["secretvalue.id"],
        ),
        sa.ForeignKeyConstraint(
            ["test_traversal_id"],
            ["testtraversal.id"],
        ),
        sa.PrimaryKeyConstraint("secret_value_id", "test_traversal_id"),
    )
    op.create_table(
        "testrun",
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "test_traversal_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "browser_config_id",
            AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "run_type",
            runtype_enum,
            nullable=True,
        ),
        sa.Column("origin", runorigin_enum, nullable=True),
        sa.Column("repair_was_needed", sa.Boolean(), nullable=False),
        sa.Column(
            "current_state",
            runstate_enum,
            nullable=True,
        ),
        sa.Column(
            "run_gif",
            AutoString(length=500),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["browser_config_id"], ["browserconfig.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["test_traversal_id"], ["testtraversal.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "action",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "brain_state_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("idx_in_brain_state", sa.Integer(), nullable=False),
        sa.Column("action", sa.JSON(), nullable=True),
        sa.Column("dom_element_data", sa.JSON(), nullable=True),
        sa.Column("valid", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["brain_state_id"], ["brainstate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cost",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "test_run_id",
            AutoString(length=255),
            nullable=True,
        ),
        sa.Column(
            "project_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "model_type",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("cost_per_token", sa.Float(), nullable=False),
        sa.Column("input_token_num", sa.Integer(), nullable=False),
        sa.Column("completion_token_num", sa.Integer(), nullable=False),
        sa.Column("cost_in_dollars", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["testrun.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "historyelement",
        sa.Column("id", AutoString(length=255), nullable=False),
        sa.Column(
            "test_run_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "action_id",
            AutoString(length=255),
            nullable=False,
        ),
        sa.Column("action_started_at", sa.DateTime(), nullable=False),
        sa.Column("action_finished_at", sa.DateTime(), nullable=False),
        sa.Column(
            "history_element_state",
            historyelementstate_enum,
            nullable=True,
        ),
        sa.Column("screenshot", AutoString(), nullable=True),
        sa.ForeignKeyConstraint(["action_id"], ["action.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_run_id"], ["testrun.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("historyelement")
    op.drop_table("cost")
    op.drop_table("action")
    op.drop_table("testrun")
    op.drop_table("secretvaluetesttraversal")
    op.drop_table("brainstate")
    op.drop_table("testtraversal")
    op.drop_table("testcasebrowserconfig")
    op.drop_table("testcase")
    op.drop_table("secretvalue")
    op.drop_table("document")
    op.drop_table("browserconfig")
    op.drop_table("project")

    # Drop enum types
    bind = op.get_bind()

    runtype_enum = postgresql.ENUM(name="runtype", create_type=False)
    runorigin_enum = postgresql.ENUM(name="runorigin", create_type=False)
    runstate_enum = postgresql.ENUM(name="runstate", create_type=False)
    historyelementstate_enum = postgresql.ENUM(name="historyelementstate", create_type=False)

    runtype_enum.drop(bind, checkfirst=True)
    runorigin_enum.drop(bind, checkfirst=True)
    runstate_enum.drop(bind, checkfirst=True)
    historyelementstate_enum.drop(bind, checkfirst=True)
