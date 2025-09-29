from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    ForeignKey,
    Integer,
    String,
    DateTime,
    datetime,
)
from .user import User
from .movie import Movie
from app.extensions import db
from datetime import timezone


class Comment(db.Model):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True
    )
    comment_text: Mapped[str] = mapped_column(String(1000), nullable=False)

    # ZMIENIONE: DateTime z timezone=True i UTC default
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="comments")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="comments")

    replies: Mapped[list["CommentReply"]] = relationship(
        "CommentReply", back_populates="main_comment", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Comment(id={self.comment_id}, user_id={self.user_id}, movie_id={self.movie_id}, text='{self.comment_text}')>"

    def serialize(
        self,
        include_user=False,
        include_movie=False,
        include_rating=False,
        include_replies=False,
    ):
        result = {
            "id": self.comment_id,
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "text": self.comment_text,
            # ZMIENIONE: Dodaj 'Z' dla UTC lub użyj pełnego ISO format z timezone
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_user and self.user:
            result["user"] = {
                "id": self.user.user_id,
                "username": self.user.username,
                "profile_picture": (
                    self.user.profile_picture
                    if hasattr(self.user, "profile_picture")
                    else None
                ),
            }

        if include_movie and self.movie:
            result["movie"] = {"id": self.movie.movie_id, "title": self.movie.title}

        if include_rating and self.user and hasattr(self.user, "ratings"):
            user_rating = next(
                (
                    rating
                    for rating in self.user.ratings
                    if rating.movie_id == self.movie_id
                ),
                None,
            )
            if user_rating:
                result["user_rating"] = {
                    "rating": user_rating.rating,
                    "rated_at": (
                        user_rating.rated_at.isoformat()
                        if user_rating.rated_at
                        else None
                    ),
                }
            else:
                result["user_rating"] = None

        if include_replies:
            result["replies"] = [
                reply.serialize(include_users=True) for reply in self.replies
            ]
            result["replies_count"] = len(self.replies)

        return result
