from .base import Base, Mapped, mapped_column, ForeignKey, Integer


class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)

    def __repr__(self):
        return f"<FavoriteMovie(user_id={self.user_id}, movie_id={self.movie_id})>"
    
    def serialize(self):
        return {
            "user_id": self.user_id,
            "movie_id": self.movie_id
        }
