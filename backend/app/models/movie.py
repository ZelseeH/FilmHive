from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    String,
    Integer,
    Date,
    DateTime,
)
from flask import url_for
from sqlalchemy import desc, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property, deferred, joinedload
from app.extensions import db


def _get_photo_url(photo_url: str, folder: str):
    if not photo_url:
        return None
    if photo_url.startswith("http://") or photo_url.startswith("https://"):
        return photo_url
    return url_for("static", filename=f"{folder}/{photo_url}", _external=True)


class Movie(db.Model):
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    release_date: Mapped[Date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    poster_url: Mapped[str] = mapped_column(String(255))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    country: Mapped[str] = mapped_column(String(100))
    original_language: Mapped[str] = mapped_column(String(50))
    trailer_url: Mapped[str] = mapped_column(String(255), nullable=True)

    genres = relationship(
        "Genre",
        secondary="movies_genres",
        back_populates="movies",
        lazy="joined",
    )

    actors = relationship(
        "Actor",
        secondary="movie_actors",
        back_populates="movies",
        lazy="select",
    )
    directors = relationship(
        "Director",
        secondary="movie_directors",
        back_populates="movies",
        lazy="select",
    )
    ratings = relationship(
        "Rating",
        back_populates="movie",
        lazy="select",
        cascade="all, delete",
    )
    comments = relationship(
        "Comment", back_populates="movie", lazy="select", cascade="all, delete"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="movie", lazy="select", cascade="all, delete"
    )

    _average_rating = None
    _rating_count = None

    def __repr__(self):
        return f"<Movie(id={self.movie_id}, title='{self.title}', release_date={self.release_date})>"

    @property
    def average_rating(self):
        if self._average_rating is None:
            from sqlalchemy import func
            from sqlalchemy.orm import Session
            from app.models.rating import Rating

            session = Session.object_session(self)
            if session:
                avg_rating = (
                    session.query(func.avg(Rating.rating))
                    .filter(Rating.movie_id == self.movie_id)
                    .scalar()
                )
                self._average_rating = (
                    float(avg_rating) if avg_rating is not None else None
                )
            else:
                self._average_rating = None
        return self._average_rating

    @property
    def rating_count(self):
        if self._rating_count is None:
            from sqlalchemy import func
            from sqlalchemy.orm import Session
            from app.models.rating import Rating

            session = Session.object_session(self)
            if session:
                self._rating_count = (
                    session.query(func.count(Rating.rating_id))
                    .filter(Rating.movie_id == self.movie_id)
                    .scalar()
                )
            else:
                self._rating_count = 0
        return self._rating_count

    def _get_poster_url(self):
        if not self.poster_url:
            return None
        if self.poster_url.startswith("http://") or self.poster_url.startswith(
            "https://"
        ):
            return self.poster_url
        return url_for("static", filename=f"posters/{self.poster_url}", _external=True)

    def serialize(
        self,
        include_genres=False,
        include_actors=False,
        include_actors_roles=False,
        include_directors=False,
        include_ratings=False,
        include_comments=False,
    ):
        result = {
            "id": self.movie_id,
            "title": self.title,
            "release_date": (
                self.release_date.isoformat() if self.release_date else None
            ),
            "description": self.description,
            "poster_url": self._get_poster_url(),
            "duration_minutes": self.duration_minutes,
            "country": self.country,
            "original_language": self.original_language,
            "trailer_url": self.trailer_url,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
            "user_rating": getattr(self, "_user_rating", None),
        }

        if include_genres:
            result["genres"] = [
                {"id": genre.genre_id, "name": genre.genre_name}
                for genre in self.genres
            ]

        if include_actors:
            if include_actors_roles:
                from sqlalchemy import select
                from sqlalchemy.orm import Session
                from app.models.movie_actor import MovieActor

                session = Session.object_session(self)
                actors_with_roles = []

                stmt = select(MovieActor).where(MovieActor.movie_id == self.movie_id)
                roles_map = {
                    ma.actor_id: ma.movie_role for ma in session.execute(stmt).scalars()
                }

                for actor in self.actors:
                    actors_with_roles.append(
                        {
                            "id": actor.actor_id,
                            "name": actor.actor_name,
                            "role": roles_map.get(actor.actor_id, ""),
                            "photo_url": (
                                _get_photo_url(actor.photo_url, "actors")
                                if actor.photo_url
                                else None
                            ),
                        }
                    )
                result["actors"] = actors_with_roles
            else:
                result["actors"] = [
                    {
                        "id": actor.actor_id,
                        "name": actor.actor_name,
                        "photo_url": (
                            _get_photo_url(actor.photo_url, "actors")
                            if actor.photo_url
                            else None
                        ),
                    }
                    for actor in self.actors
                ]

        if include_directors:
            result["directors"] = [
                {
                    "id": director.director_id,
                    "name": director.director_name,
                    "photo_url": (
                        _get_photo_url(director.photo_url, "directors")
                        if director.photo_url
                        else None
                    ),
                }
                for director in self.directors
            ]

        if include_ratings:
            result["ratings"] = [rating.serialize() for rating in self.ratings]

        if include_comments:
            result["comments"] = [comment.serialize() for comment in self.comments]

        return result

    def serialize_basic(self):
        return {
            "id": self.movie_id,
            "title": self.title,
            "poster_url": self._get_poster_url(),
        }

    @classmethod
    def get_with_ratings(cls, session, page=1, per_page=10):
        from app.models.rating import Rating

        subq = (
            session.query(
                Rating.movie_id,
                func.avg(Rating.rating).label("avg_rating"),
                func.count(Rating.rating_id).label("rating_count"),
            )
            .group_by(Rating.movie_id)
            .subquery()
        )

        query = (
            session.query(Movie, subq.c.avg_rating, subq.c.rating_count)
            .outerjoin(subq, Movie.movie_id == subq.c.movie_id)
            .options(joinedload(Movie.genres))
            .order_by(desc(subq.c.avg_rating))
        )

        total = query.count()
        movies_with_ratings = query.offset((page - 1) * per_page).limit(per_page).all()

        result = []
        for movie, avg_rating, rating_count in movies_with_ratings:
            movie._average_rating = (
                float(avg_rating) if avg_rating is not None else None
            )
            movie._rating_count = rating_count or 0
            result.append(movie)

        return result, total
