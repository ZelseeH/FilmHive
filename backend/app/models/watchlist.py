from .base import Base, Mapped, mapped_column, ForeignKey, Integer, relationship

class Watchlist(Base):
    __tablename__ = "watchlist"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True, index=True)

    
    user: Mapped["User"] = relationship("User", back_populates="watchlist")
    movie: Mapped["Movie"] = relationship("Movie")

    def __repr__(self):
        return f"<Watchlist(user_id={self.user_id}, movie_id={self.movie_id})>"
    
    def serialize(self):
        return {
            "user_id": self.user_id,
            "movie_id": self.movie_id
        }
