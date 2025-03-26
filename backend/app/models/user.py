from .base import Base, Mapped, mapped_column, relationship, String, Integer, DateTime, datetime, Boolean
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1=admin, 2=moderator, 3=user
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relacje
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    activity_logs: Mapped[list["UserActivityLog"]] = relationship("UserActivityLog", back_populates="user")
    login_activities: Mapped[list["LoginActivity"]] = relationship("LoginActivity", back_populates="user")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="user")
    watchlist: Mapped[list["Watchlist"]] = relationship("Watchlist", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', email='{self.email}', role={self.role})>"
    
    def set_password(self, password):
        """Ustawia zahashowane hasło dla użytkownika"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Sprawdza, czy podane hasło jest poprawne"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Sprawdza, czy użytkownik ma uprawnienia administratora"""
        return self.role == 1
    
    @property
    def is_moderator(self):
        """Sprawdza, czy użytkownik ma uprawnienia moderatora"""
        return self.role <= 2  # Admin też ma uprawnienia moderatora
    
    def update_last_login(self):
        """Aktualizuje datę ostatniego logowania"""
        self.last_login = datetime.utcnow()
    
    def serialize(self, include_ratings=False, include_comments=False, include_activity_logs=False, 
                  include_login_activities=False, include_recommendations=False, include_watchlist=False):
        """Serializuje obiekt użytkownika do formatu JSON"""
        result = {
            "id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "profile_picture": self.profile_picture,
            "bio": self.bio
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
        
        if include_watchlist:
            result["watchlist"] = [watchlist_item.serialize() for watchlist_item in self.watchlist]
        
        return result
