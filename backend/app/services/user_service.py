from app.repositories.user_repository import UserRepository
from app.services.database import db
from werkzeug.exceptions import BadRequest
from app.utils.file_handlers import save_user_image
from app.services.user_activity_service import (
    log_password_change,
    log_username_change,
    log_email_change,
    log_profile_update,
)

user_repo = UserRepository(db.session)


def get_user_by_id(user_id):
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return None
        return user.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania użytkownika o ID {user_id}: {str(e)}")


def get_user_by_username(username):
    try:
        user = user_repo.get_by_username(username)
        if not user:
            return None
        return user.serialize()
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania użytkownika o nazwie {username}: {str(e)}"
        )


def update_user_profile(user_id, data):
    try:
        if "email" in data and not data["email"]:
            raise ValueError("Email nie może być pusty")

        if "name" in data and not data["name"].strip():
            raise ValueError("Imię i nazwisko nie może być puste")

        # 🔥 POBIERZ STARE DANE PRZED AKTUALIZACJĄ
        user = user_repo.get_by_id(user_id)
        if not user:
            return None

        old_username = user.username
        old_email = user.email

        # Aktualizuj profil
        user = user_repo.update_profile(user_id, data)
        if not user:
            return None

        # 🔥 LOGUJ ZMIANY
        # Zmiana nazwy użytkownika
        if "username" in data and data["username"] != old_username:
            log_username_change(user_id, old_username, data["username"])

        # Zmiana emailu
        if "email" in data and data["email"] != old_email:
            log_email_change(user_id, old_email, data["email"])

        # Aktualizacja profilu (bio lub inne dane)
        profile_fields = ["bio", "name"]
        if any(field in data for field in profile_fields):
            log_profile_update(user_id)

        return user.serialize()
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(
            f"Błąd podczas aktualizacji profilu użytkownika o ID {user_id}: {str(e)}"
        )


def change_user_password(user_id, current_password, new_password):
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return False

        if not user.check_password(current_password):
            return False

        if len(new_password) < 8:
            raise ValueError("Nowe hasło musi mieć co najmniej 8 znaków")

        # Zmień hasło
        result = user_repo.change_password(user_id, new_password)

        if result:
            log_password_change(user_id)

        return result
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Błąd podczas zmiany hasła: {str(e)}")


def upload_profile_picture(user_id, file):
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return None

        file_path = save_user_image(file, user.username, "profile_picture")
        if not file_path:
            raise ValueError(
                "Nieprawidłowy format pliku. Dozwolone formaty: png, jpg, jpeg, gif, webp"
            )

        updated_user = user_repo.update_profile_picture(user_id, file_path)

        # 🔥 LOGUJ ZMIANĘ ZDJĘCIA PROFILOWEGO
        log_profile_update(user_id)

        return updated_user.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas przesyłania zdjęcia profilowego: {str(e)}")


def upload_background_image(user_id, file, position=None):
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            return None

        print(f"Przesyłanie zdjęcia w tle dla użytkownika {user.username}")

        if position is None:
            position = {"x": 50, "y": 50}

        print(f"Pozycja zdjęcia: {position}")

        file_path = save_user_image(file, user.username, "background_image", position)
        print(f"Zapisana ścieżka do pliku: {file_path}")

        if not file_path:
            raise ValueError(
                "Nieprawidłowy format pliku. Dozwolone formaty: png, jpg, jpeg, gif, webp"
            )

        updated_user = user_repo.update_background_image(user_id, file_path)
        print(
            f"Zaktualizowana ścieżka do zdjęcia w tle: {updated_user.background_image}"
        )

        # 🔥 LOGUJ ZMIANĘ ZDJĘCIA TŁA
        log_profile_update(user_id)

        return updated_user.serialize()
    except Exception as e:
        print(f"Błąd podczas przesyłania zdjęcia w tle: {str(e)}")
        raise


def update_user_email(user_id, new_email, current_password):
    """Aktualizuje email użytkownika z weryfikacją hasła i loguje aktywność"""
    try:
        if not new_email or not new_email.strip():
            raise ValueError("Email nie może być pusty")

        if not current_password:
            raise ValueError("Obecne hasło jest wymagane")

        # Aktualizuj email w repository (z weryfikacją hasła)
        result = user_repo.update_email(user_id, new_email.strip(), current_password)
        if not result:
            return None

        user, old_email = result

        # 🔥 LOGUJ ZMIANĘ EMAILU
        log_email_change(user_id, old_email, new_email)

        return user.serialize()

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji emailu: {str(e)}")


def get_recent_rated_movies(user_id, limit=5):
    """Pobiera ostatnio ocenione filmy z poprawnie przetworzonymi URL-ami posterów"""
    try:
        # ✅ UŻYWA user_repo - ma już poprawne przetwarzanie URL-ów
        recent_movies = user_repo.get_recent_rated_movies(user_id, limit)
        return recent_movies
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania ostatnich ocenionych filmów: {str(e)}"
        )


def get_recent_favorite_movies(user_id, limit=6):
    """Pobiera ostatnio polubione filmy z poprawnie przetworzonymi URL-ami posterów"""
    try:
        # ✅ POPRAWKA: Używa user_repo zamiast FavoriteMovieService
        movies = user_repo.get_recent_favorite_movies(user_id, limit)
        return movies  # Już przetworzone przez repository
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania ostatnich polubionych filmów: {str(e)}"
        )


def get_recent_watchlist_movies(user_id, limit=6):
    """Pobiera ostatnie filmy z watchlisty z poprawnie przetworzonymi URL-ami posterów"""
    try:
        # ✅ POPRAWKA: Używa user_repo zamiast WatchlistService
        movies = user_repo.get_recent_watchlist_movies(user_id, limit)
        return movies  # Już przetworzone przez repository
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania ostatnich filmów z listy do obejrzenia: {str(e)}"
        )


def search_users(query, page=1, per_page=10):
    try:
        result = user_repo.search(query, page, per_page)
        users = result["users"]
        pagination = result["pagination"]
        serialized_users = [user.serialize() for user in users]
        return {"users": serialized_users, "pagination": pagination}
    except Exception as e:
        raise Exception(f"Błąd podczas wyszukiwania użytkowników: {str(e)}")


def get_basic_statistics():
    """Pobiera podstawowe statystyki użytkowników"""
    try:
        stats = user_repo.get_basic_statistics()
        return stats
    except Exception as e:
        raise Exception(f"Nie udało się pobrać statystyk: {str(e)}")


def get_dashboard_data():
    """Pobiera dane dashboard dla użytkowników"""
    try:
        dashboard_data = user_repo.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise Exception(f"Nie udało się pobrać danych dashboard: {str(e)}")


def get_all_rated_movies(user_id):
    """Pobierz wszystkie ocenione filmy użytkownika (bez limitu)"""
    try:
        movies = user_repo.get_all_rated_movies(user_id)
        return movies
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania wszystkich ocenionych filmów: {str(e)}"
        )


def get_all_favorite_movies(user_id):
    """Pobierz wszystkie ulubione filmy użytkownika (bez limitu)"""
    try:
        movies = user_repo.get_all_favorite_movies(user_id)
        return movies
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania wszystkich ulubionych filmów: {str(e)}"
        )


def get_all_watchlist_movies(user_id):
    """Pobierz wszystkie filmy z watchlisty użytkownika (bez limitu)"""
    try:
        movies = user_repo.get_all_watchlist_movies(user_id)
        return movies
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania wszystkich filmów z watchlisty: {str(e)}"
        )
