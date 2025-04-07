"""add_gender

Revision ID: 4aeddaf9fff9
Revises: ee82d783601e
Create Date: 2025-04-07 14:46:58.894041

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4aeddaf9fff9"
down_revision: Union[str, None] = "ee82d783601e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Dodaj kolumnę gender z domyślną wartością 'M', aby uniknąć błędu NOT NULL
    op.add_column(
        "actors",
        sa.Column("gender", sa.String(length=1), nullable=False, server_default="M"),
    )
    # Usuń domyślną wartość po dodaniu kolumny, jeśli nie ma być domyślna na stałe
    op.alter_column("actors", "gender", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("actors", "gender")
