from app.repositories.rating_repository import RatingRepository
from app.services.database import db
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.user import User
from datetime import datetime

rating_repo = RatingRepository(db.session)


def get_rating_by_id(rating_id):
    """Pobiera ocenę na podstawie ID."""
    try:
        rating = rating_repo.get_by_id(rating_id)
        return (
            rating.serialize(include_user=True, include_movie=True) if rating else None
        )
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania oceny: {str(e)}")


def get_user_rating_for_movie(user_id, movie_id):
    """Pobiera ocenę użytkownika dla danego filmu."""
    try:
        rating = rating_repo.get_by_user_and_movie(user_id, movie_id)
        return rating.rating if rating else None
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania oceny użytkownika: {str(e)}")


def get_movie_ratings(movie_id, page=1, per_page=10):
    """Pobiera oceny dla danego filmu."""
    try:
        result = rating_repo.get_movie_ratings(movie_id, page, per_page)
        return {
            "ratings": [
                rating.serialize(include_user=True) for rating in result["ratings"]
            ],
            "pagination": result["pagination"],
        }
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania ocen filmu: {str(e)}")


def get_user_ratings(user_id, page=1, per_page=10):
    """Pobiera oceny danego użytkownika."""
    try:
        result = rating_repo.get_user_ratings(user_id, page, per_page)
        return {
            "ratings": [
                rating.serialize(include_movie=True) for rating in result["ratings"]
            ],
            "pagination": result["pagination"],
        }
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania ocen użytkownika: {str(e)}")


def get_movie_average_rating(movie_id):
    """Pobiera średnią ocenę dla danego filmu."""
    try:
        avg_rating = rating_repo.get_movie_average_rating(movie_id)
        return {"average_rating": avg_rating if avg_rating is not None else 0.0}
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania średniej oceny: {str(e)}")


def get_movie_rating_count(movie_id):
    """Pobiera liczbę ocen dla danego filmu."""
    try:
        count = rating_repo.get_movie_rating_count(movie_id)
        return {"rating_count": count}
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania liczby ocen: {str(e)}")


def get_movie_rating_stats(movie_id):
    """Pobiera statystyki ocen dla danego filmu."""
    try:
        stats = rating_repo.get_movie_rating_stats(movie_id)
        return stats
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania statystyk ocen: {str(e)}")


def create_rating(user_id, movie_id, rating_value):
    """Tworzy nową ocenę lub aktualizuje istniejącą."""
    try:
        if not (1 <= rating_value <= 10):
            raise ValueError("Ocena musi być w zakresie od 1 do 10")

        user, movie = db.session.get(User, user_id), db.session.get(Movie, movie_id)
        if not user or not movie:
            raise ValueError("Użytkownik lub film nie istnieje")

        existing_rating = rating_repo.get_by_user_and_movie(user_id, movie_id)
        if existing_rating:
            existing_rating.rating = rating_value
            existing_rating.rated_at = datetime.utcnow()
            db.session.commit()
            result = existing_rating.serialize()
        else:
            new_rating = Rating(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating_value,
                rated_at=datetime.utcnow(),
            )
            rating_repo.add(new_rating)
            result = new_rating.serialize()

        stats = get_movie_rating_stats(movie_id)
        result.update(stats)
        return result
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Błąd podczas tworzenia oceny: {str(e)}")


def update_rating(rating_id, new_rating_value, user_id):
    """Aktualizuje ocenę użytkownika."""
    try:
        if not (1 <= new_rating_value <= 10):
            raise ValueError("Ocena musi być w zakresie od 1 do 10")

        rating = rating_repo.get_by_id(rating_id)
        if not rating:
            raise ValueError("Ocena nie istnieje")

        if rating.user_id != user_id:
            raise ValueError("Nie masz uprawnień do edycji tej oceny")

        updated_rating = rating_repo.update(rating_id, new_rating_value)
        result = updated_rating.serialize()
        stats = get_movie_rating_stats(updated_rating.movie_id)
        result.update(stats)
        return result
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji oceny: {str(e)}")


def delete_rating(rating_id, user_id):
    """Usuwa ocenę, jeśli użytkownik jest właścicielem."""
    try:
        rating = rating_repo.get_by_id(rating_id)
        if not rating:
            raise ValueError("Ocena nie istnieje")

        if rating.user_id != user_id:
            raise ValueError("Nie masz uprawnień do usunięcia tej oceny")

        movie_id = rating.movie_id
        success = rating_repo.delete(rating_id)
        result = {"success": success}
        if success:
            stats = get_movie_rating_stats(movie_id)
            result.update(stats)
        return result
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Błąd podczas usuwania oceny: {str(e)}")
