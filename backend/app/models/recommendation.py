from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    ForeignKey,
    Integer,
    Float,
    String,
    DateTime,
    datetime,
    validates,
)
from app.extensions import db


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "movie_id", name="unique_user_movie_recommendation"
        ),
    )

    @validates("score")
    def validate_score(self, key, value):
        if not (0 <= value <= 1):
            raise ValueError("Score must be between 0 and 1.")
        return value

    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="recommendations")

    def __repr__(self):
        return (
            f"<Recommendation(id={self.recommendation_id}, user_id={self.user_id}, "
            f"movie_id={self.movie_id}, score={self.score})>"
        )

    def serialize(self, include_user=False, include_movie=False):
        result = {
            "id": self.recommendation_id,
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_user and self.user:
            result["user"] = {"id": self.user.user_id, "username": self.user.username}

        if include_movie and self.movie:
            result["movie"] = {"id": self.movie.movie_id, "title": self.movie.title}

        return result
