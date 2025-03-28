from .base import Base, Mapped, mapped_column, relationship, String, Integer, Date, DateTime
from .recommendation import Recommendation

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