from .base import Base, Mapped, mapped_column, relationship, ForeignKey, Integer, String, DateTime, datetime
from .user  import User

class LoginActivity(Base):
    __tablename__ = "login_activities"

    login_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(50))
    login_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_agent: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="Success")

    user: Mapped["User"] = relationship("User", back_populates="login_activities")

    def __repr__(self):
        return f"<LoginActivity(login_id={self.login_id}, user_id={self.user_id}, ip_address='{self.ip_address}', timestamp={self.login_timestamp})>"