from .base import Base, Mapped, mapped_column, relationship, ForeignKey, Integer, String, DateTime, datetime
from .user import User

class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    activity: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return f"<UserActivityLog(log_id={self.log_id}, user_id={self.user_id}, activity='{self.activity}', timestamp={self.activity_timestamp})>"
    
    def serialize(self, include_user=False):
        result = {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "activity": self.activity,
            "activity_timestamp": self.activity_timestamp.isoformat() if self.activity_timestamp else None
        }
        
        if include_user and self.user:
            result["user"] = {
                "id": self.user.user_id,
                "username": self.user.username
            }
            
        return result
