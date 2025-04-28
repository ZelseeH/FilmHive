from app.repositories.user_repository import UserRepository
from app.services.database import db
from werkzeug.exceptions import BadRequest
from app.utils.file_handlers import save_user_image

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

        user = user_repo.update_profile(user_id, data)
        if not user:
            return None

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

        return user_repo.change_password(user_id, new_password)
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

        return updated_user.serialize()
    except Exception as e:
        print(f"Błąd podczas przesyłania zdjęcia w tle: {str(e)}")
        raise


def get_recent_rated_movies(user_id, limit=5):
    try:
        recent_movies = user_repo.get_recent_rated_movies(user_id, limit)
        return recent_movies
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania ostatnich ocenionych filmów: {str(e)}"
        )


def get_recent_favorite_movies(user_id, limit=6):
    try:
        from app.services.favorite_movie_service import FavoriteMovieService

        favorite_service = FavoriteMovieService()
        return favorite_service.get_recent_favorite_movies(user_id, limit)
    except Exception as e:
        raise Exception(
            f"Błąd podczas pobierania ostatnich polubionych filmów: {str(e)}"
        )


def get_recent_watchlist_movies(user_id, limit=6):
    try:
        from app.services.watchlist_service import WatchlistService

        watchlist_service = WatchlistService()
        result = watchlist_service.get_recent_watchlist_movies(user_id, limit)
        return result.get("movies", [])
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
