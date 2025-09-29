from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    String,
    Integer,
    Date,
    datetime,
    Enum,
)
from .movie import Movie
import enum
from flask import url_for
from app.extensions import db, Base


class Gender(enum.Enum):
    M = "M"
    K = "K"


class Director(db.Model):
    __tablename__ = "directors"

    director_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    director_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    birth_date: Mapped[datetime] = mapped_column(Date)
    birth_place: Mapped[str] = mapped_column(String(255))
    biography: Mapped[str] = mapped_column(String(2000))
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=True)

    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movie_directors", back_populates="directors"
    )

    def __repr__(self):
        return f"<Director(id={self.director_id}, name='{self.director_name}', birth_date={self.birth_date})>"

    def serialize(self, include_movies=False):
        from flask import url_for

        def is_full_url(url):
            return url and (url.startswith("http://") or url.startswith("https://"))

        if is_full_url(self.photo_url):
            photo = self.photo_url
        elif self.photo_url:
            photo = url_for(
                "static", filename=f"directors/{self.photo_url}", _external=True
            )
        else:
            photo = None

        result = {
            "id": self.director_id,
            "name": self.director_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "birth_place": self.birth_place,
            "biography": self.biography,
            "photo_url": photo,
            "gender": self.gender.value if self.gender else None,
        }

        if include_movies:
            result["movies"] = [
                {"id": movie.movie_id, "title": movie.title} for movie in self.movies
            ]

        return result
