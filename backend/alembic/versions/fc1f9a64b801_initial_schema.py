"""Initial schema

Revision ID: fc1f9a64b801
Revises: fff2f3183de2
Create Date: 2025-11-03 09:11:12.252104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc1f9a64b801'
down_revision: Union[str, Sequence[str], None] = 'fff2f3183de2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
