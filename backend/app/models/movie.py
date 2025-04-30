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


class Movie(Base):
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
    genres = relationship("Genre", secondary="movies_genres", back_populates="movies")
    actors = relationship("Actor", secondary="movie_actors", back_populates="movies")
    directors = relationship(
        "Director", secondary="movie_directors", back_populates="movies"
    )
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="movie"
    )

    @property
    def average_rating(self):
        from sqlalchemy import func
        from sqlalchemy.orm import Session
        from app.models.rating import Rating

        session = Session.object_session(self)
        avg_rating = (
            session.query(func.avg(Rating.rating))
            .filter(Rating.movie_id == self.movie_id)
            .scalar()
        )
        return float(avg_rating) if avg_rating is not None else None

    @property
    def rating_count(self):
        from sqlalchemy import func
        from sqlalchemy.orm import Session
        from app.models.rating import Rating

        session = Session.object_session(self)
        return (
            session.query(func.count(Rating.rating_id))
            .filter(Rating.movie_id == self.movie_id)
            .scalar()
        )

    def __repr__(self):
        return f"<Movie(id={self.movie_id}, title='{self.title}', release_date={self.release_date})>"

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
            "poster_url": (
                url_for("static", filename=f"posters/{self.poster_url}", _external=True)
                if self.poster_url
                else None
            ),
            "duration_minutes": self.duration_minutes,
            "country": self.country,
            "original_language": self.original_language,
            "trailer_url": self.trailer_url,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
<<<<<<< Updated upstream
=======
            "user_rating": getattr(self, "_user_rating", None),
>>>>>>> Stashed changes
        }

        if include_genres:
            result["genres"] = [
                {"genre_id": genre.genre_id, "genre_name": genre.genre_name}
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
                                url_for(
                                    "static",
                                    filename=f"actors/{actor.photo_url}",
                                    _external=True,
                                )
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
                            url_for(
                                "static",
                                filename=f"actors/{actor.photo_url}",
                                _external=True,
                            )
                            if actor.photo_url
                            else None
                        ),
                    }
                    for actor in self.actors
                ]

        if include_directors:
            result["directors"] = [
                {"id": director.director_id, "name": director.director_name}
                for director in self.directors
            ]

        if include_ratings:
            result["ratings"] = [rating.serialize() for rating in self.ratings]

        if include_comments:
            result["comments"] = [comment.serialize() for comment in self.comments]

        return result
<<<<<<< Updated upstream
=======

    def serialize_basic(self):
        return {
            "id": self.movie_id,
            "title": self.title,
            "poster_url": (
                url_for("static", filename=f"posters/{self.poster_url}", _external=True)
                if self.poster_url
                else None
            ),
        }


@classmethod
def get_with_ratings(cls, session, page=1, per_page=10, genre_id=None, user_id=None):
    from app.models.rating import Rating

    # Podzapytanie do ocen
    subq = (
        session.query(
            Rating.movie_id,
            func.avg(Rating.rating).label("avg_rating"),
            func.count(Rating.rating_id).label("rating_count"),
        )
        .group_by(Rating.movie_id)
        .subquery()
    )

    # Główne zapytanie do filmów
    query = (
        session.query(Movie, subq.c.avg_rating, subq.c.rating_count)
        .outerjoin(subq, Movie.movie_id == subq.c.movie_id)
        .options(joinedload(Movie.genres))
        .order_by(desc(subq.c.avg_rating))
    )

    # Filtr po gatunku, jeśli podano genre_id
    if genre_id:
        query = query.join(Movie.genres).filter(Genre.genre_id == genre_id)

    total = query.count()
    movies_with_ratings = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for movie, avg_rating, rating_count in movies_with_ratings:
        movie._average_rating = float(avg_rating) if avg_rating is not None else None
        movie._rating_count = rating_count or 0
        result.append(movie)

    return result, total
>>>>>>> Stashed changes
