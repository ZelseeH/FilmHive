from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    datetime,
)
from .user import User
from .comment import Comment
from .comment_reply import CommentReply
from app.extensions import db
from datetime import timezone


class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.comment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reply_id: Mapped[int] = mapped_column(
        ForeignKey("comment_replies.reply_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relacje
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="notifications"
    )
    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id])
    comment: Mapped["Comment"] = relationship("Comment")
    reply: Mapped["CommentReply"] = relationship("CommentReply")

    def __repr__(self):
        return f"<Notification(id={self.notification_id}, user={self.user_id}, from={self.from_user_id})>"

    def get_movie_id(self):
        """Pobiera movie_id przez relacje"""
        try:
            if self.reply_id and self.reply:
                # POPRAWKA: użyj main_comment zamiast comment
                return (
                    self.reply.main_comment.movie_id
                    if self.reply.main_comment
                    else None
                )
            elif self.comment_id and self.comment:
                # comment_id -> comment -> movie_id
                return self.comment.movie_id
            return None
        except Exception as e:
            from flask import current_app

            current_app.logger.error(
                f"Error getting movie_id for notification {self.notification_id}: {e}"
            )
            return None

    def get_movie_url(self):
        """Generuje URL do filmu z wątkiem"""
        try:
            movie_id = self.get_movie_id()
            if movie_id:
                if self.reply_id:
                    return f"/movie/{movie_id}#reply-{self.reply_id}"
                else:
                    return f"/movie/{movie_id}#comment-{self.comment_id}"
            return None
        except Exception as e:
            from flask import current_app

            current_app.logger.error(
                f"Error getting movie_url for notification {self.notification_id}: {e}"
            )
            return None

    def mark_as_read(self):
        """Oznacza jako przeczytane"""
        try:
            self.is_read = True
            db.session.commit()
        except Exception as e:
            from flask import current_app

            current_app.logger.error(
                f"Error marking notification {self.notification_id} as read: {e}"
            )
            db.session.rollback()
            raise

    def serialize(self, include_users=False, include_movie=False):
        result = {
            "id": self.notification_id,
            "user_id": self.user_id,
            "from_user_id": self.from_user_id,
            "comment_id": self.comment_id,
            "reply_id": self.reply_id,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_users:
            try:
                if self.from_user:
                    result["from_user"] = {
                        "id": self.from_user.user_id,
                        "username": self.from_user.username,
                        "profile_picture": getattr(
                            self.from_user, "profile_picture", None
                        ),
                    }
                else:
                    result["from_user"] = None
            except Exception as e:
                from flask import current_app

                current_app.logger.error(
                    f"Error serializing from_user for notification {self.notification_id}: {e}"
                )
                result["from_user"] = None

        if include_movie:
            try:
                movie_id = self.get_movie_id()
                if movie_id:
                    from .movie import Movie

                    movie = Movie.query.get(movie_id)
                    if movie:
                        result["movie"] = {
                            "id": movie.movie_id,
                            "title": movie.title,
                            "poster_url": getattr(movie, "poster_url", None),
                        }
                    else:
                        result["movie"] = None
                else:
                    result["movie"] = None

                result["movie_url"] = self.get_movie_url()
            except Exception as e:
                from flask import current_app

                current_app.logger.error(
                    f"Error serializing movie data for notification {self.notification_id}: {e}"
                )
                result["movie"] = None
                result["movie_url"] = None

        return result
