from .base import Base, Mapped, mapped_column, relationship, String, Integer
from .movie import Movie
from app.extensions import db


class Genre(db.Model):
    __tablename__ = "genres"

    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    genre_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movies_genres", back_populates="genres"
    )

    def __repr__(self):
        return f"<Genre(id={self.genre_id}, name='{self.genre_name}')>"

    def serialize(self):
        return {"id": self.genre_id, "name": self.genre_name}
