from .base import Base, Mapped, mapped_column, relationship, String, Integer, Date, datetime
from .movie import Movie

class Director(Base):
    __tablename__ = "directors"

    director_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    director_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    birth_date: Mapped[datetime] = mapped_column(Date)
    birth_place: Mapped[str] = mapped_column(String(255))
    biography: Mapped[str] = mapped_column(String(2000))

    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movie_directors", back_populates="directors"
    )

    def __repr__(self):
        return f"<Director(id={self.director_id}, name='{self.director_name}', birth_date={self.birth_date})>"

    def serialize(self, include_movies=False):
        result = {
            "id": self.director_id,
            "name": self.director_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "birth_place": self.birth_place,
            "biography": self.biography
        }
        
        if include_movies:
            result["movies"] = [{"id": movie.movie_id, "title": movie.title} for movie in self.movies]
            
        return result
