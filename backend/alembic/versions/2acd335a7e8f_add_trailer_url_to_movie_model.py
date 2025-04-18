"""Add trailer_url to Movie model

Revision ID: 2acd335a7e8f
Revises: 52bbd2dc01a4
Create Date: 2025-04-01 12:12:43.893519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2acd335a7e8f'
down_revision: Union[str, None] = '52bbd2dc01a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('trailer_url', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movies', 'trailer_url')
    # ### end Alembic commands ###
