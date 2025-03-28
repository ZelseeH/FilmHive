from .base import Base, Mapped, mapped_column, relationship, ForeignKey, Integer, Float, String, DateTime, datetime, validates
from .user import User
from .movie import Movie

class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    algorithm_used: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @validates('score')
    def validate_score(self, key, value):
        if not (0 <= value <= 1):
            raise ValueError("Score must be between 0 and 1.")
        return value

    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.recommendation_id}, user_id={self.user_id}, movie_id={self.movie_id}, score={self.score})>"