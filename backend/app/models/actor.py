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
import enum  
from .movie import Movie
from flask import url_for


class Gender(enum.Enum):
    M = "M"
    K = "K"


class Actor(Base):
    __tablename__ = "actors"

    actor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    birth_date: Mapped[datetime] = mapped_column(Date)
    birth_place: Mapped[str] = mapped_column(String(255))
    biography: Mapped[str] = mapped_column(String(2000))
    photo_url: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  

    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=True)

    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movie_actors", back_populates="actors"
    )

    def __repr__(self):
        return f"<Actor(id={self.actor_id}, name='{self.actor_name}', birth_date={self.birth_date})>"

    def serialize(self, include_movies=False):
        from flask import url_for

        result = {
            "id": self.actor_id,
            "name": self.actor_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "birth_place": self.birth_place,
            "biography": self.biography,
            "photo_url": (
                url_for("static", filename=f"actors/{self.photo_url}", _external=True)
                if self.photo_url
                else None
            ),
            "gender": (self.gender.value if self.gender else None),
        }

        if include_movies:
            result["movies"] = [
                {"id": movie.movie_id, "title": movie.title} for movie in self.movies
            ]

        return result
