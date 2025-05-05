from .base import Base, Mapped, mapped_column, ForeignKey, Integer
from app.extensions import db


class MovieDirector(db.Model):
    __tablename__ = "movie_directors"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.director_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    def __repr__(self):
        return (
            f"<MovieDirector(movie_id={self.movie_id}, director_id={self.director_id})>"
        )

    def serialize(self):
        return {"movie_id": self.movie_id, "director_id": self.director_id}
