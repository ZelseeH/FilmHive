"""add_profile_and_background_images

Revision ID: be998d7808d2
Revises: f4b1d2be9a27
Create Date: 2025-04-05 11:54:15.966000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be998d7808d2'
down_revision: Union[str, None] = 'f4b1d2be9a27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
