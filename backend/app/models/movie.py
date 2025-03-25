from .base import Base, Mapped, mapped_column, relationship, String, Integer, Date, DateTime
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

    genres = relationship("Genre", secondary="movies_genres", back_populates="movies")
    actors = relationship("Actor", secondary="movie_actors", back_populates="movies")
    directors = relationship("Director", secondary="movie_directors", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="movie")

    def __repr__(self):
        return f"<Movie(id={self.movie_id}, title='{self.title}', release_date={self.release_date})>"
    
    def serialize(self, include_genres=False, include_actors=False, include_directors=False, include_ratings=False, include_comments=False):
        result = {
            "id": self.movie_id,
            "title": self.title,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "description": self.description,
            "poster_url": url_for('static', filename=f'posters/{self.poster_url}', _external=True) if self.poster_url else None,
            "duration_minutes": self.duration_minutes,
            "country": self.country,
            "original_language": self.original_language
        }
        
        if include_genres:
            result["genres"] = [{"id": genre.genre_id, "name": genre.genre_name} for genre in self.genres]
            
        if include_actors:
            result["actors"] = [{"id": actor.actor_id, "name": actor.actor_name} for actor in self.actors]
            
        if include_directors:
            result["directors"] = [{"id": director.director_id, "name": director.director_name} for director in self.directors]
            
        if include_ratings:
            result["ratings"] = [rating.serialize() for rating in self.ratings]
            
        if include_comments:
            result["comments"] = [comment.serialize() for comment in self.comments]
            
        return result
