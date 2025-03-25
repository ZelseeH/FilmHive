from .base import Base, Mapped, mapped_column, relationship, String, Integer, Date, datetime
from .movie import Movie

class Actor(Base):
    __tablename__ = "actors"
    
    actor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    birth_date: Mapped[datetime] = mapped_column(Date)
    birth_place: Mapped[str] = mapped_column(String(255))
    biography: Mapped[str] = mapped_column(String(2000))

    movies: Mapped[list["Movie"]] = relationship(
        "Movie", secondary="movie_actors", back_populates="actors"
    )

    def __repr__(self):
        return f"<Actor(id={self.actor_id}, name='{self.actor_name}', birth_date={self.birth_date})>"

    def serialize(self, include_movies=False):
        result = {
            "id": self.actor_id,
            "name": self.actor_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "birth_place": self.birth_place,
            "biography": self.biography
        }
        
        if include_movies:
            result["movies"] = [{"id": movie.movie_id, "title": movie.title} for movie in self.movies]
            
        return result
