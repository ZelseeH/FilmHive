"""commentreply

Revision ID: b2446a2afcc4
Revises: b436c8e6106e
Create Date: 2025-09-05 15:51:02.280498

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b2446a2afcc4"
down_revision: Union[str, None] = "b436c8e6106e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create comment_replies table
    op.create_table(
        "comment_replies",
        sa.Column("reply_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_main", sa.Integer(), nullable=False),
        sa.Column("comment_main_id", sa.Integer(), nullable=False),
        sa.Column("id_reply", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["comment_main_id"], ["comments.comment_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["id_main"], ["users.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_reply"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("reply_id"),
    )
    op.create_index("ix_comment_replies_id_main", "comment_replies", ["id_main"])
    op.create_index(
        "ix_comment_replies_comment_main_id", "comment_replies", ["comment_main_id"]
    )
    op.create_index("ix_comment_replies_id_reply", "comment_replies", ["id_reply"])

    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("from_user_id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("reply_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["comments.comment_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["from_user_id"], ["users.user_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["reply_id"], ["comment_replies.reply_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("notification_id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_from_user_id", "notifications", ["from_user_id"])
    op.create_index("ix_notifications_comment_id", "notifications", ["comment_id"])
    op.create_index("ix_notifications_reply_id", "notifications", ["reply_id"])


def downgrade() -> None:
    # Drop notifications
    op.drop_index("ix_notifications_reply_id", "notifications")
    op.drop_index("ix_notifications_comment_id", "notifications")
    op.drop_index("ix_notifications_from_user_id", "notifications")
    op.drop_index("ix_notifications_user_id", "notifications")
    op.drop_table("notifications")

    # Drop comment_replies
    op.drop_index("ix_comment_replies_id_reply", "comment_replies")
    op.drop_index("ix_comment_replies_comment_main_id", "comment_replies")
    op.drop_index("ix_comment_replies_id_main", "comment_replies")
    op.drop_table("comment_replies")
