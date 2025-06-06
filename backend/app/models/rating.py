from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    ForeignKey,
    Integer,
    DateTime,
    datetime,
    UniqueConstraint,
    validates,
)
from app.extensions import db


class Rating(db.Model):
    __tablename__ = "ratings"

    rating_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    rated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @validates("rating")
    def validate_rating(self, key, value):
        if not (0 <= value <= 10):
            raise ValueError("Rating must be between 0 and 10.")
        return value

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_user_movie_rating"),
    )

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="ratings")

    def __repr__(self):
        return f"<Rating(id={self.rating_id}, user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"

    def serialize(self, include_user=False, include_movie=False):
        result = {
            "id": self.rating_id,
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "rating": self.rating,
            "rated_at": self.rated_at.isoformat() if self.rated_at else None,
        }

        if include_user and self.user:
            result["user"] = {"id": self.user.user_id, "username": self.user.username}

        if include_movie and self.movie:
            result["movie"] = {"id": self.movie.movie_id, "title": self.movie.title}

        return result
