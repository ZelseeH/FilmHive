"""add_background_image

Revision ID: 6127d446217b
Revises: d906dcf1b2d3
Create Date: 2025-04-05 12:00:04.833914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6127d446217b'
down_revision: Union[str, None] = 'd906dcf1b2d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
