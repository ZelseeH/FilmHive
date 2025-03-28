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