from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    datetime,
)
from .user import User
from .comment import Comment
from app.extensions import db
from datetime import timezone


class CommentReply(db.Model):
    __tablename__ = "comment_replies"

    reply_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_main: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    comment_main_id: Mapped[int] = mapped_column(
        ForeignKey("comments.comment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_reply: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    main_user: Mapped["User"] = relationship(
        "User", foreign_keys=[id_main], back_populates="received_replies"
    )
    reply_user: Mapped["User"] = relationship(
        "User", foreign_keys=[id_reply], back_populates="sent_replies"
    )
    main_comment: Mapped["Comment"] = relationship("Comment", back_populates="replies")

    def __repr__(self):
        return f"<CommentReply(id={self.reply_id}, main_user={self.id_main}, reply_user={self.id_reply})>"

    def serialize(self, include_users=False):
        result = {
            "id": self.reply_id,
            "main_user_id": self.id_main,
            "comment_id": self.comment_main_id,
            "reply_user_id": self.id_reply,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_users:
            if self.main_user:
                result["main_user"] = {
                    "id": self.main_user.user_id,
                    "username": self.main_user.username,
                }
            if self.reply_user:
                result["reply_user"] = {
                    "id": self.reply_user.user_id,
                    "username": self.reply_user.username,
                    "profile_picture": (
                        self.reply_user.profile_picture
                        if hasattr(self.reply_user, "profile_picture")
                        else None
                    ),
                }

                # DODAJ OCENĘ UŻYTKOWNIKA DLA FILMU
                # Pobierz ocenę użytkownika dla filmu z głównego komentarza
                if self.main_comment and self.main_comment.movie_id:
                    try:
                        from .rating import Rating  # Import lokalny

                        user_rating = Rating.query.filter_by(
                            user_id=self.reply_user.user_id,
                            movie_id=self.main_comment.movie_id,
                        ).first()

                        result["user_rating"] = (
                            user_rating.rating if user_rating else None
                        )
                    except Exception as e:
                        # W przypadku błędu ustaw None
                        result["user_rating"] = None

        return result
