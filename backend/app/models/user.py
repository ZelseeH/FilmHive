from .base import (
    Base,
    Mapped,
    mapped_column,
    relationship,
    String,
    Integer,
    DateTime,
    datetime,
    Boolean,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
import os
import json
from flask import current_app


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False
    )  # 1=admin, 2=moderator, 3=user
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)
    background_image: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(String(500), nullable=True)

    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    activity_logs: Mapped[list["UserActivityLog"]] = relationship(
        "UserActivityLog", back_populates="user"
    )
    login_activities: Mapped[list["LoginActivity"]] = relationship(
        "LoginActivity", back_populates="user"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="user"
    )
    watchlist: Mapped[list["Watchlist"]] = relationship(
        "Watchlist", back_populates="user"
    )

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', name='{self.name}', email='{self.email}', role={self.role})>"

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
        return self.role <= 2

    def update_last_login(self):
        """Aktualizuje datę ostatniego logowania"""
        self.last_login = datetime.utcnow()

    def serialize(
        self,
        include_ratings=False,
        include_comments=False,
        include_activity_logs=False,
        include_login_activities=False,
        include_recommendations=False,
        include_watchlist=False,
    ):
        """Serializuje obiekt użytkownika do formatu JSON"""
        # Sprawdź, czy istnieje plik z pozycją dla zdjęcia w tle
        background_position = {"x": 50, "y": 50}  # Domyślna pozycja
        if self.background_image:
            bg_path = self.background_image.lstrip("/static/")
            position_file = bg_path.replace(".jpg", "_position.json").replace(
                ".png", "_position.json"
            )
            position_path = os.path.join(current_app.root_path, "static", position_file)
            if os.path.exists(position_path):
                try:
                    with open(position_path, "r") as f:
                        background_position = json.load(f)
                except:
                    pass

        result = {
            "id": self.user_id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "registration_date": (
                self.registration_date.isoformat() if self.registration_date else None
            ),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "profile_picture": (
                url_for(
                    "static",
                    filename=self.profile_picture.lstrip("/static/"),
                    _external=True,
                )
                if self.profile_picture
                else None
            ),
            "background_image": (
                url_for(
                    "static",
                    filename=(
                        self.background_image.lstrip("/static/")
                        if self.background_image.startswith("/static/")
                        else self.background_image
                    ),
                    _external=True,
                )
                if self.background_image
                else None
            ),
            "background_position": background_position,
            "bio": self.bio,
        }
        print(
            f"Zwracany obiekt zawiera background_position: {result['background_position']}"
        )

        if include_ratings:
            result["ratings"] = [rating.serialize() for rating in self.ratings]

        if include_comments:
            result["comments"] = [comment.serialize() for comment in self.comments]

        if include_activity_logs:
            result["activity_logs"] = [log.serialize() for log in self.activity_logs]

        if include_login_activities:
            result["login_activities"] = [
                activity.serialize() for activity in self.login_activities
            ]

        if include_recommendations:
            result["recommendations"] = [
                recommendation.serialize() for recommendation in self.recommendations
            ]

        if include_watchlist:
            result["watchlist"] = [
                watchlist_item.serialize() for watchlist_item in self.watchlist
            ]

        return result
