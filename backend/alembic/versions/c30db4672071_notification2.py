"""notification2

Revision ID: c30db4672071
Revises: 242804c8244a
Create Date: 2025-09-11 14:19:08.825017

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c30db4672071"
down_revision: Union[str, None] = "242804c8244a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NIC NIE RÓB - poprzednia migracja już dodała notification_type
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # NIC NIE RÓB - poprzednia migracja już obsłużyła notification_type
    pass
