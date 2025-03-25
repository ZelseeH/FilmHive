from .base import Base, Mapped, mapped_column, ForeignKey, Integer


class MovieGenre(Base):
    __tablename__ = "movies_genres"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.genre_id", ondelete="CASCADE"), primary_key=True, index=True)

    def __repr__(self):
        return f"<MovieGenre(movie_id={self.movie_id}, genre_id={self.genre_id})>"
    
    def serialize(self):
        return {
            "movie_id": self.movie_id,
            "genre_id": self.genre_id
        }
