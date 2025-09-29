from sqlalchemy import or_, func
from flask import url_for
from app.models.user import User
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.favorite_movie import FavoriteMovie
from app.models.watchlist import Watchlist


def _get_poster_url_for_movie(poster_url):
    """Pomocnicza funkcja do przetwarzania URL posterów filmów"""
    if not poster_url:
        return None
    # Sprawdź czy to już pełny URL (TMDB)
    if poster_url.startswith(("http://", "https://")):
        return poster_url
    # Dla lokalnych plików dodaj pełną ścieżkę
    return url_for("static", filename=f"posters/{poster_url}", _external=True)


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
        """Aktualizuje profil użytkownika z debugowaniem"""
        print(f"=== DEBUG UPDATE_PROFILE ===")
        print(f"User ID: {user_id}")
        print(f"Dane do aktualizacji: {data}")

        user = self.get_by_id(user_id)
        if not user:
            print(f"ERROR: Nie znaleziono użytkownika o ID: {user_id}")
            return None

        print(f"Znaleziono użytkownika: {user.username} ({user.email})")

        # Walidacja i aktualizacja username
        if "username" in data and data["username"] != user.username:
            print(f"Zmiana username z '{user.username}' na '{data['username']}'")

            if not data["username"].strip():
                print("ERROR: Nazwa użytkownika nie może być pusta")
                raise ValueError("Nazwa użytkownika nie może być pusta")

            existing_user = self.get_by_username_or_email(data["username"])
            if existing_user:
                print(
                    f"Znaleziono istniejącego użytkownika z username: {existing_user.user_id}"
                )

            if existing_user and existing_user.user_id != user.user_id:
                print("ERROR: Nazwa użytkownika jest już zajęta")
                raise ValueError("Nazwa użytkownika jest już zajęta")

            user.username = data["username"]
            print(f"Username zaktualizowany na: {user.username}")

        # Walidacja i aktualizacja email
        if "email" in data and data["email"] != user.email:
            print(f"Zmiana email z '{user.email}' na '{data['email']}'")

            if not data["email"].strip():
                print("ERROR: Email nie może być pusty")
                raise ValueError("Email nie może być pusty")

            # Podstawowa walidacja formatu email
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, data["email"]):
                print(f"ERROR: Nieprawidłowy format emailu: {data['email']}")
                raise ValueError("Nieprawidłowy format emailu")

            existing_user = self.get_by_username_or_email(data["email"])
            if existing_user:
                print(
                    f"Znaleziono istniejącego użytkownika z email: {existing_user.user_id}"
                )

            if existing_user and existing_user.user_id != user.user_id:
                print("ERROR: Email jest już zajęty")
                raise ValueError("Email jest już zajęty")

            user.email = data["email"]
            print(f"Email zaktualizowany na: {user.email}")

        # Aktualizacja pozostałych pól
        for field in ["name", "bio", "profile_picture", "is_active"]:
            if field in data:
                old_value = getattr(user, field)
                setattr(user, field, data[field])
                print(f"{field} zaktualizowane z '{old_value}' na '{data[field]}'")

        # Zapisz zmiany
        try:
            print("Zapisywanie zmian do bazy danych...")
            self.session.commit()
            print("✅ Zmiany zapisane pomyślnie!")
            print(f"Zaktualizowany użytkownik: {user.username} ({user.email})")
            print("=== END DEBUG ===")
            return user
        except Exception as e:
            print(f"❌ BŁĄD podczas zapisywania: {str(e)}")
            self.session.rollback()
            print("Rollback wykonany")
            print("=== END DEBUG ===")
            raise Exception(f"Błąd podczas zapisywania zmian: {str(e)}")

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
        """Pobiera ostatnio ocenione filmy z poprawnymi URL-ami posterów"""
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
                "poster_url": _get_poster_url_for_movie(
                    movie.poster_url
                ),  # ✅ POPRAWKA
                "rating": rating.rating,
                "rated_at": rating.rated_at.isoformat() if rating.rated_at else None,
            }
            for rating, movie in results
        ]

    def get_recent_favorite_movies(self, user_id, limit=6):
        """Pobiera ostatnio polubione filmy z poprawnymi URL-ami posterów"""
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
                "poster_url": _get_poster_url_for_movie(
                    movie.poster_url
                ),  # ✅ POPRAWKA
                "added_at": fav.added_at.isoformat() if fav.added_at else None,
            }
            for fav, movie in results
        ]

    def get_recent_watchlist_movies(self, user_id, limit=6):
        """Pobiera ostatnie filmy z watchlisty z poprawnymi URL-ami posterów"""
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
                "poster_url": _get_poster_url_for_movie(
                    movie.poster_url
                ),  # ✅ POPRAWKA
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

    # Metody do obsługi panelu administratora
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

    def update_email(self, user_id, new_email, current_password):
        """Aktualizuje email użytkownika z weryfikacją hasła"""
        print(f"=== DEBUG UPDATE_EMAIL REPOSITORY ===")
        print(f"User ID: {user_id}, New email: {new_email}")

        user = self.get_by_id(user_id)
        if not user:
            print(f"ERROR: Nie znaleziono użytkownika o ID: {user_id}")
            return None

        # 🔥 WERYFIKACJA OBECNEGO HASŁA
        if not user.check_password(current_password):
            print("ERROR: Nieprawidłowe obecne hasło")
            raise ValueError("Nieprawidłowe obecne hasło")

        old_email = user.email
        print(f"Zmiana email z '{old_email}' na '{new_email}'")

        # Sprawdź czy email nie jest już zajęty
        existing_user = self.get_by_username_or_email(new_email)
        if existing_user and existing_user.user_id != user.user_id:
            print("ERROR: Email jest już zajęty")
            raise ValueError("Email jest już zajęty")

        # Podstawowa walidacja formatu email
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, new_email):
            print(f"ERROR: Nieprawidłowy format emailu: {new_email}")
            raise ValueError("Nieprawidłowy format emailu")

        user.email = new_email

        try:
            print("Zapisywanie zmiany email do bazy danych...")
            self.session.commit()
            print("✅ Email zaktualizowany pomyślnie!")
            print("=== END DEBUG ===")
            return user, old_email
        except Exception as e:
            print(f"❌ BŁĄD podczas zapisywania: {str(e)}")
            self.session.rollback()
            print("=== END DEBUG ===")
            raise Exception(f"Błąd podczas zapisywania zmian: {str(e)}")

    def get_recent_active_users(self, limit=10):
        """Pobierz ostatnio aktywnych użytkowników"""
        return (
            self.session.query(User)
            .filter(User.last_login != None)
            .order_by(User.last_login.desc())
            .limit(limit)
            .all()
        )

    def get_by_email(self, email):
        """Pobierz użytkownika na podstawie adresu email"""
        return self.session.query(User).filter(User.email == email).first()

    # OAUTH METHODS
    def get_by_google_id(self, google_id):
        """Znajdź użytkownika po Google ID"""
        return self.session.query(User).filter_by(google_id=google_id).first()

    def get_by_facebook_id(self, facebook_id):
        """Znajdź użytkownika po Facebook ID"""
        return self.session.query(User).filter_by(facebook_id=facebook_id).first()

    def get_by_github_id(self, github_id):
        """Znajdź użytkownika po GitHub ID"""
        return self.session.query(User).filter_by(github_id=github_id).first()

    def get_by_oauth_provider(self, provider, provider_id):
        """Uniwersalna metoda do znajdowania użytkownika po OAuth provider"""
        if provider == "google":
            return self.get_by_google_id(provider_id)
        elif provider == "facebook":
            return self.get_by_facebook_id(provider_id)
        elif provider == "github":
            return self.get_by_github_id(provider_id)
        return None

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki użytkowników"""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta

            # Podstawowe liczby użytkowników
            total_users = self.session.query(User).count()

            # Użytkownicy według ról
            admins_count = (
                self.session.query(User).filter(User.role == 1).count()
            )  # Admin
            moderators_count = (
                self.session.query(User).filter(User.role == 2).count()
            )  # Moderator
            regular_users_count = (
                self.session.query(User).filter(User.role == 3).count()
            )  # Regular user

            # Aktywne konta
            active_users = (
                self.session.query(User).filter(User.is_active == True).count()
            )
            inactive_users = (
                self.session.query(User).filter(User.is_active == False).count()
            )

            # Użytkownicy OAuth vs zwykli
            oauth_users = (
                self.session.query(User).filter(User.oauth_created == True).count()
            )
            regular_login_users = (
                self.session.query(User).filter(User.oauth_created == False).count()
            )

            # Użytkownicy z ostatnich 30 dni
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_users = (
                self.session.query(User)
                .filter(User.registration_date >= thirty_days_ago)
                .count()
            )

            # Użytkownicy z ostatnich 7 dni
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_users = (
                self.session.query(User)
                .filter(User.registration_date >= week_ago)
                .count()
            )

            # Użytkownicy z profilowymi zdjęciami
            with_profile_pictures = (
                self.session.query(User)
                .filter(User.profile_picture.isnot(None))
                .count()
            )

            # Użytkownicy z bio
            with_bio = (
                self.session.query(User)
                .filter(User.bio.isnot(None), User.bio != "")
                .count()
            )

            return {
                "total_users": total_users,
                "role_distribution": {
                    "admins": admins_count,
                    "moderators": moderators_count,
                    "regular_users": regular_users_count,
                },
                "account_status": {
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "active_percentage": (
                        round((active_users / total_users * 100), 2)
                        if total_users > 0
                        else 0
                    ),
                },
                "authentication_types": {
                    "oauth_users": oauth_users,
                    "regular_login_users": regular_login_users,
                    "oauth_percentage": (
                        round((oauth_users / total_users * 100), 2)
                        if total_users > 0
                        else 0
                    ),
                },
                "registration_trends": {
                    "recent_users_30_days": recent_users,
                    "weekly_users": weekly_users,
                },
                "profile_completion": {
                    "with_profile_pictures": with_profile_pictures,
                    "with_bio": with_bio,
                    "profile_picture_percentage": (
                        round((with_profile_pictures / total_users * 100), 2)
                        if total_users > 0
                        else 0
                    ),
                    "bio_percentage": (
                        round((with_bio / total_users * 100), 2)
                        if total_users > 0
                        else 0
                    ),
                },
            }

        except Exception as e:
            print(f"Błąd podczas pobierania podstawowych statystyk: {e}")
            raise

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla użytkowników"""
        try:
            from sqlalchemy import func, extract
            from datetime import datetime, timedelta

            # Podstawowe statystyki
            basic_stats = self.get_basic_statistics()

            # Rejestracje według miesięcy (ostatnie 12 miesięcy)
            monthly_registrations = []
            for i in range(12):
                month_start = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
                month_end = (month_start + timedelta(days=32)).replace(
                    day=1
                ) - timedelta(days=1)

                count = (
                    self.session.query(User)
                    .filter(
                        User.registration_date >= month_start,
                        User.registration_date <= month_end,
                    )
                    .count()
                )

                monthly_registrations.append(
                    {"month": month_start.strftime("%Y-%m"), "count": count}
                )

            # Ostatnie logowania (aktywność użytkowników)
            last_login_stats = []
            time_ranges = [
                ("last_24h", timedelta(hours=24)),
                ("last_7_days", timedelta(days=7)),
                ("last_30_days", timedelta(days=30)),
                ("last_90_days", timedelta(days=90)),
            ]

            for label, delta in time_ranges:
                threshold = datetime.utcnow() - delta
                count = (
                    self.session.query(User)
                    .filter(User.last_login >= threshold)
                    .count()
                )
                last_login_stats.append({"period": label, "active_users": count})

            # Najaktywniejsze konta (według ostatniego logowania)
            most_active_users = (
                self.session.query(User)
                .filter(User.last_login.isnot(None))
                .order_by(User.last_login.desc())
                .limit(10)
                .all()
            )

            # Ostatnio zarejestrowani użytkownicy
            recent_users = (
                self.session.query(User)
                .order_by(User.registration_date.desc())
                .limit(10)
                .all()
            )

            # Rozkład według dostawców OAuth
            oauth_providers = []
            providers = ["google", "facebook", "github"]
            for provider in providers:
                count = (
                    self.session.query(User)
                    .filter(User.oauth_provider == provider)
                    .count()
                )
                if count > 0:
                    oauth_providers.append({"provider": provider, "count": count})

            return {
                "statistics": basic_stats,
                "monthly_registrations": list(reversed(monthly_registrations)),
                "user_activity": last_login_stats,
                "oauth_providers": oauth_providers,
                "most_active_users": [
                    {
                        "id": user.user_id,
                        "username": user.username,
                        "last_login": (
                            user.last_login.isoformat() if user.last_login else None
                        ),
                        "role": user.role,
                        "profile_picture": user.profile_picture,
                    }
                    for user in most_active_users
                ],
                "recent_users": [
                    {
                        "id": user.user_id,
                        "username": user.username,
                        "registration_date": (
                            user.registration_date.isoformat()
                            if user.registration_date
                            else None
                        ),
                        "role": user.role,
                        "oauth_provider": user.oauth_provider,
                        "profile_picture": user.profile_picture,
                    }
                    for user in recent_users
                ],
            }

        except Exception as e:
            print(f"Błąd podczas pobierania danych dashboard: {e}")
            raise

    def get_all_rated_movies(self, user_id):
        """Pobiera wszystkie ocenione filmy użytkownika (bez limitu)"""
        results = (
            self.session.query(Rating, Movie)
            .join(Movie, Rating.movie_id == Movie.movie_id)
            .filter(Rating.user_id == user_id)
            .order_by(Rating.rated_at.desc())
            .all()
        )

        print(f"Pobrano wszystkie {len(results)} ocenione filmy użytkownika {user_id}")

        return [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "poster_url": _get_poster_url_for_movie(movie.poster_url),
                "rating": rating.rating,
                "rated_at": rating.rated_at.isoformat() if rating.rated_at else None,
            }
            for rating, movie in results
        ]

    def get_all_favorite_movies(self, user_id):
        """Pobiera wszystkie ulubione filmy użytkownika (bez limitu)"""
        results = (
            self.session.query(FavoriteMovie, Movie)
            .join(Movie, FavoriteMovie.movie_id == Movie.movie_id)
            .filter(FavoriteMovie.user_id == user_id)
            .order_by(FavoriteMovie.added_at.desc())
            .all()
        )

        print(f"Pobrano wszystkie {len(results)} ulubione filmy użytkownika {user_id}")

        return [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "poster_url": _get_poster_url_for_movie(movie.poster_url),
                "added_at": fav.added_at.isoformat() if fav.added_at else None,
            }
            for fav, movie in results
        ]

    def get_all_watchlist_movies(self, user_id):
        """Pobiera wszystkie filmy z watchlisty użytkownika (bez limitu)"""
        results = (
            self.session.query(Watchlist, Movie)
            .join(Movie, Watchlist.movie_id == Movie.movie_id)
            .filter(Watchlist.user_id == user_id)
            .order_by(Watchlist.added_at.desc())
            .all()
        )

        print(
            f"Pobrano wszystkie {len(results)} filmy z watchlisty użytkownika {user_id}"
        )

        return [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "poster_url": _get_poster_url_for_movie(movie.poster_url),
                "added_at": (
                    watchlist.added_at.isoformat() if watchlist.added_at else None
                ),
            }
            for watchlist, movie in results
        ]
