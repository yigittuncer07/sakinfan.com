"""add_sohbet_board

Revision ID: e1420d65a9cc
Revises: 2a76fc05a865
Create Date: 2026-08-26 21:19:05.036797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1420d65a9cc'
down_revision: Union[str, Sequence[str], None] = '2a76fc05a865'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # insert Sohbet right after Site Hakkında (which has display_order 1)
    op.execute(
        "INSERT INTO boards (name, description, display_order) "
        "VALUES ('Sohbet', 'Genel sohbet ve muhabbet.', 2)"
    )
    # shift all subsequent boards down by 1 to maintain logical ordering
    op.execute(
        "UPDATE boards SET display_order = display_order + 1 "
        "WHERE name NOT IN ('Site Hakkında', 'Sohbet')"
    )

def downgrade() -> None:
    op.execute("DELETE FROM boards WHERE name = 'Sohbet'")
    op.execute(
        "UPDATE boards SET display_order = display_order - 1 "
        "WHERE name != 'Site Hakkında'"
    )