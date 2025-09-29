"""notificationFinal

Revision ID: b66fe2649af4
Revises: c30db4672071
Create Date: 2025-09-11 14:21:58.795781

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b66fe2649af4"
down_revision: Union[str, None] = "c30db4672071"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Usuń niepotrzebną kolumnę notification_type
    op.drop_column("notifications", "notification_type")


def downgrade() -> None:
    """Downgrade schema."""
    # Przywróć kolumnę notification_type
    op.add_column(
        "notifications",
        sa.Column(
            "notification_type",
            sa.VARCHAR(length=50),
            nullable=False,
            server_default="new_comment",
        ),
    )
