from .base import Base, Mapped, mapped_column, ForeignKey, Integer, DateTime, datetime


class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FavoriteMovie(user_id={self.user_id}, movie_id={self.movie_id})>"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "added_at": self.added_at.isoformat() if self.added_at else None,
        }
