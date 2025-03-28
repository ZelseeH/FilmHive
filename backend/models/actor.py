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