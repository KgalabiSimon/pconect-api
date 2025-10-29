"""drop_programme_column_from_users

Revision ID: 98cf45de0b9e
Revises: 5062f0e186e5
Create Date: 2025-10-23 22:16:24.680420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98cf45de0b9e'
down_revision: Union[str, None] = '5062f0e186e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'programme')


def downgrade() -> None:
    op.add_column('users', sa.Column('programme', sa.String(length=100)))
