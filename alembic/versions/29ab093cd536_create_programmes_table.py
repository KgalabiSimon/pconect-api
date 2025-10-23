"""create programmes table

Revision ID: 29ab093cd536
Revises: 44c6673f1f94
Create Date: 2025-10-23 22:08:23.281771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '29ab093cd536'
down_revision: Union[str, None] = '44c6673f1f94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'programmes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('name', sa.String(length=100), unique=True, nullable=False)
    )



def downgrade() -> None:
    op.drop_table('programmes')
