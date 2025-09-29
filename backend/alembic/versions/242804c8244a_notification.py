"""notification

Revision ID: 242804c8244a
Revises: b2446a2afcc4
Create Date: 2025-09-11 14:11:47.511971

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "242804c8244a"
down_revision: Union[str, None] = "b2446a2afcc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Dodaj tylko notification_type do istniejącej tabeli notifications
    op.add_column(
        "notifications",
        sa.Column("notification_type", sa.String(length=50), nullable=True),
    )

    # Ustaw domyślne wartości dla istniejących rekordów
    op.execute(
        "UPDATE notifications SET notification_type = 'legacy' WHERE notification_type IS NULL"
    )

    # Teraz ustaw NOT NULL constraint
    op.alter_column("notifications", "notification_type", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Usuń kolumnę notification_type
    op.drop_column("notifications", "notification_type")
