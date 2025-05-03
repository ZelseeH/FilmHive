from sqlalchemy import or_, func
from flask import url_for
from app.models.user import User
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.favorite_movie import FavoriteMovie
from app.models.watchlist import Watchlist


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        return self.session.get(User, user_id)

    def get_by_username_or_email(self, identifier):
        return (
            self.session.query(User)
            .filter((User.username == identifier) | (User.email == identifier))
            .first()
        )

    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def add(self, user):
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user):
        self.session.commit()
        return user

    def update_profile(self, user_id, data):
        user = self.get_by_id(user_id)
        if not user:
            return None

        if "username" in data and data["username"] != user.username:
            existing_user = self.get_by_username_or_email(data["username"])
            if existing_user and existing_user.user_id != user.user_id:
                raise ValueError("Nazwa użytkownika jest już zajęta")
            user.username = data["username"]

        if "email" in data and data["email"] != user.email:
            existing_user = self.get_by_username_or_email(data["email"])
            if existing_user and existing_user.user_id != user.user_id:
                raise ValueError("Email jest już zajęty")
            user.email = data["email"]

        if "name" in data:
            user.name = data["name"]

        if "bio" in data:
            user.bio = data["bio"]

        if "profile_picture" in data:
            user.profile_picture = data["profile_picture"]

        if "is_active" in data:
            user.is_active = data["is_active"]

        self.session.commit()
        return user

    def change_password(self, user_id, new_password):
        user = self.get_by_id(user_id)
        if not user:
            return False
        user.set_password(new_password)
        self.session.commit()
        return True

    def update_profile_picture(self, user_id, profile_picture_path):
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.profile_picture = profile_picture_path
        self.session.commit()
        return user

    def update_background_image(self, user_id, background_image_path):
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.background_image = background_image_path
        self.session.commit()
        return user

    def get_recent_rated_movies(self, user_id, limit=6):
        results = (
            self.session.query(Rating, Movie)
            .join(Movie, Rating.movie_id == Movie.movie_id)
            .filter(Rating.user_id == user_id)
            .order_by(Rating.rated_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "poster_url": (
                    url_for(
                        "static", filename=f"posters/{movie.poster_url}", _external=True
                    )
                    if movie.poster_url
                    else None
                ),
                "rating": rating.rating,
                "rated_at": rating.rated_at.isoformat() if rating.rated_at else None,
            }
            for rating, movie in results
        ]

    def get_recent_favorite_movies(self, user_id, limit=6):
        results = (
            self.session.query(FavoriteMovie, Movie)
            .join(Movie, FavoriteMovie.movie_id == Movie.movie_id)
            .filter(FavoriteMovie.user_id == user_id)
            .order_by(FavoriteMovie.added_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "poster_url": (
                    url_for(
                        "static", filename=f"posters/{movie.poster_url}", _external=True
                    )
                    if movie.poster_url
                    else None
                ),
                "added_at": fav.added_at.isoformat() if fav.added_at else None,
            }
            for fav, movie in results
        ]

    def get_recent_watchlist_movies(self, user_id, limit=6):
        results = (
            self.session.query(Watchlist, Movie)
            .join(Movie, Watchlist.movie_id == Movie.movie_id)
            .filter(Watchlist.user_id == user_id)
            .order_by(Watchlist.added_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "poster_url": (
                    url_for(
                        "static", filename=f"posters/{movie.poster_url}", _external=True
                    )
                    if movie.poster_url
                    else None
                ),
                "added_at": (
                    watchlist.added_at.isoformat() if watchlist.added_at else None
                ),
            }
            for watchlist, movie in results
        ]

    def search(self, query, page=1, per_page=10):
        search_query = f"%{query}%"
        base = self.session.query(User).filter(
            or_(
                User.username.ilike(search_query),
                User.name.ilike(search_query),
            )
        )
        total = base.count()
        users = (
            base.order_by(User.username)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        total_pages = (total + per_page - 1) // per_page
        return {
            "users": users,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    # Nowe metody do obsługi panelu administratora

    def get_all(self):
        """Pobierz wszystkich użytkowników"""
        return self.session.query(User).all()

    def get_all_paginated(self, page=1, per_page=20):
        """Pobierz paginowaną listę użytkowników"""
        return self.session.query(User).paginate(page=page, per_page=per_page)

    def count_all(self):
        """Policz wszystkich użytkowników"""
        return self.session.query(func.count(User.user_id)).scalar()

    def count_active(self):
        """Policz aktywnych użytkowników"""
        return (
            self.session.query(func.count(User.user_id))
            .filter(User.is_active == True)
            .scalar()
        )

    def count_by_role(self, role):
        """Policz użytkowników z określoną rolą"""
        return (
            self.session.query(func.count(User.user_id))
            .filter(User.role == role)
            .scalar()
        )

    def get_by_role(self, role):
        """Pobierz użytkowników z określoną rolą"""
        return self.session.query(User).filter(User.role == role).all()

    def change_user_role(self, user_id, new_role):
        """Zmień rolę użytkownika"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.role = new_role
        self.session.commit()
        return user

    def activate_deactivate_user(self, user_id, is_active):
        """Aktywuj lub dezaktywuj konto użytkownika"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.is_active = is_active
        self.session.commit()
        return user

    def get_user_stats(self):
        """Pobierz statystyki użytkowników dla panelu administratora"""
        total_users = self.count_all()
        active_users = self.count_active()
        admins = self.count_by_role(1)  # 1 = admin
        moderators = self.count_by_role(2)  # 2 = moderator
        regular_users = self.count_by_role(3)  # 3 = user

        return {
            "total": total_users,
            "active": active_users,
            "admins": admins,
            "moderators": moderators,
            "regular_users": regular_users,
        }

    def get_recent_users(self, limit=10):
        """Pobierz ostatnio zarejestrowanych użytkowników"""
        return (
            self.session.query(User)
            .order_by(User.registration_date.desc())
            .limit(limit)
            .all()
        )

    def get_recent_active_users(self, limit=10):
        """Pobierz ostatnio aktywnych użytkowników"""
        return (
            self.session.query(User)
            .filter(User.last_login != None)
            .order_by(User.last_login.desc())
            .limit(limit)
            .all()
        )
