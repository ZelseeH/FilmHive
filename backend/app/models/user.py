from .base import Base, Mapped, mapped_column, relationship, String, Integer, DateTime, datetime

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
    
    def serialize(self, include_ratings=False, include_comments=False, include_activity_logs=False, include_login_activities=False, include_recommendations=False):
        result = {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None
        }
        
        if include_ratings:
            result["ratings"] = [rating.serialize() for rating in self.ratings]
        
        if include_comments:
            result["comments"] = [comment.serialize() for comment in self.comments]
        
        if include_activity_logs:
            result["activity_logs"] = [log.serialize() for log in self.activity_logs]
        
        if include_login_activities:
            result["login_activities"] = [activity.serialize() for activity in self.login_activities]
        
        if include_recommendations:
            result["recommendations"] = [recommendation.serialize() for recommendation in self.recommendations]
        
        return result
