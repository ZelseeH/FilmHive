"""add_gender_enum

Revision ID: e5ac3fb776f9
Revises: 4aeddaf9fff9
Create Date: 2025-04-07 14:51:24.924912

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e5ac3fb776f9"
down_revision: Union[str, None] = "4aeddaf9fff9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First, create the enum type
    with op.get_context().autocommit_block():
        op.execute("CREATE TYPE gender AS ENUM ('M', 'K')")

    # Then alter the existing column to use the new enum type
    op.alter_column(
        "actors",
        "gender",
        existing_type=sa.VARCHAR(length=1),
        type_=sa.Enum("M", "K", name="gender", create_type=False),
        postgresql_using="gender::text::gender",
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # First convert back to VARCHAR
    op.alter_column(
        "actors",
        "gender",
        existing_type=sa.Enum("M", "K", name="gender"),
        type_=sa.VARCHAR(length=1),
        nullable=True,
    )

    # Then drop the enum type
    with op.get_context().autocommit_block():
        op.execute("DROP TYPE gender")
