"""add_programme_id_to_users

Revision ID: 5062f0e186e5
Revises: 29ab093cd536
Create Date: 2025-10-23 22:13:33.839704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5062f0e186e5'
down_revision: Union[str, None] = '29ab093cd536'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('programme_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programmes.id', ondelete='SET NULL'), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', 'programme_id')
