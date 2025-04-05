"""add_profile_and_background_images

Revision ID: d906dcf1b2d3
Revises: be998d7808d2
Create Date: 2025-04-05 11:56:49.143259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd906dcf1b2d3'
down_revision: Union[str, None] = 'be998d7808d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
