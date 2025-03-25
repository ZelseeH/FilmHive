from .base import Base, Mapped, mapped_column, relationship, ForeignKey, Integer, String, DateTime, datetime
from .user import User
from .movie import Movie

class Comment(Base):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)
    comment_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="comments")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.comment_id}, user_id={self.user_id}, movie_id={self.movie_id}, text='{self.comment_text}')>"
    
    def serialize(self, include_user=False, include_movie=False):
        result = {
            "id": self.comment_id,
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "text": self.comment_text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_user and self.user:
            result["user"] = {
                "id": self.user.user_id,
                "username": self.user.username
            }
            
        if include_movie and self.movie:
            result["movie"] = {
                "id": self.movie.movie_id,
                "title": self.movie.title
            }
            
        return result
