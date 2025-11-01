"""Add missing values to checkinstatus enum

Revision ID: 8e3762f7fa19
Revises: 69e1fbad11e3
Create Date: 2025-11-01 21:15:19.873611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e3762f7fa19'
down_revision: Union[str, None] = '69e1fbad11e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
