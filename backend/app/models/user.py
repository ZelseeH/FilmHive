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
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Nullable dla OAuth
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

    # OAuth provider IDs
    google_id: Mapped[str] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    facebook_id: Mapped[str] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    github_id: Mapped[str] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )

    # OAuth metadata
    oauth_provider: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # 'google', 'facebook', 'github'
    oauth_created: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # czy konto utworzone przez OAuth

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
        if password:  # Sprawdź czy hasło nie jest None/puste
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Sprawdza, czy podane hasło jest poprawne"""
        if not self.password_hash:  # Konto OAuth bez hasła
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 1

    @property
    def is_moderator(self):
        return self.role <= 2

    @property
    def has_password(self):
        """Sprawdza czy użytkownik ma ustawione hasło (nie jest tylko OAuth)"""
        return bool(self.password_hash)

    @property
    def is_oauth_user(self):
        """Sprawdza czy użytkownik loguje się przez OAuth"""
        return self.oauth_created or bool(
            self.google_id or self.facebook_id or self.github_id
        )

    def update_last_login(self):
        self.last_login = datetime.utcnow()

    def link_oauth_account(self, provider, provider_id):
        """Łączy istniejące konto z OAuth providerem"""
        if provider == "google":
            self.google_id = provider_id
        elif provider == "facebook":
            self.facebook_id = provider_id
        elif provider == "github":
            self.github_id = provider_id

        if not self.oauth_provider:
            self.oauth_provider = provider

    def serialize(
        self,
        include_ratings=False,
        include_comments=False,
        include_activity_logs=False,
        include_login_activities=False,
        include_recommendations=False,
        include_watchlist=False,
    ):
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
            "oauth_provider": self.oauth_provider,
            "oauth_created": self.oauth_created,
            "has_password": self.has_password,
            "is_oauth_user": self.is_oauth_user,
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
