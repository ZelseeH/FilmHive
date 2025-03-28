from .base import Base, Mapped, mapped_column, relationship, String, Integer, DateTime, datetime
from .rating import Rating
from .comment import Comment
from .user_activity_log import UserActivityLog
from .login_activity import LoginActivity
from .recommendation import Recommendation

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    activity_logs: Mapped[list["UserActivityLog"]] = relationship("UserActivityLog", back_populates="user")
    login_activities: Mapped[list["LoginActivity"]] = relationship("LoginActivity", back_populates="user")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', email='{self.email}', role={self.role})>"