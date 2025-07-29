"""update_run_state_enum

Revision ID: f3a8b9c7d2e1
Revises: e012903566e2
Create Date: 2025-07-29 12:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3a8b9c7d2e1"
down_revision: Union[str, Sequence[str], None] = "e012903566e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Step 1: Add new enum values to the existing runstate enum
    # These need to be committed before they can be used
    connection = op.get_bind()

    # Add PENDING value
    connection.execute(sa.text("ALTER TYPE runstate ADD VALUE IF NOT EXISTS 'PENDING'"))
    connection.commit()

    # Add FAILED value
    connection.execute(sa.text("ALTER TYPE runstate ADD VALUE IF NOT EXISTS 'FAILED'"))
    connection.commit()

    # Step 2: Update existing data to use new values
    # Convert STARTING -> PENDING
    connection.execute(
        sa.text(
            """
        UPDATE testrun 
        SET current_state = 'PENDING' 
        WHERE current_state = 'STARTING'
    """
        )
    )

    # Convert RUNNING -> PENDING
    connection.execute(
        sa.text(
            """
        UPDATE testrun 
        SET current_state = 'PENDING' 
        WHERE current_state = 'RUNNING'
    """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Convert back to old values
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
        UPDATE testrun 
        SET current_state = 'STARTING' 
        WHERE current_state = 'PENDING'
    """
        )
    )

    # Note: We cannot remove enum values in PostgreSQL without recreating the enum
    # For a full downgrade, you would need to recreate the enum type
