from app.repositories.rating_repository import RatingRepository
from app.services.database import db
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.user import User
from datetime import datetime

rating_repo = RatingRepository(db.session)


def get_rating_by_id(rating_id):
    try:
        rating = rating_repo.get_by_id(rating_id)
        return (
            rating.serialize(include_user=True, include_movie=True) if rating else None
        )
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania oceny: {str(e)}")


def get_user_rating_for_movie(user_id, movie_id):
    try:
        rating = rating_repo.get_by_user_and_movie(user_id, movie_id)
        return rating.rating if rating else None
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania oceny użytkownika: {str(e)}")


def get_movie_ratings(movie_id, page=1, per_page=10):
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
    try:
        avg_rating = rating_repo.get_movie_average_rating(movie_id)
        return {"average_rating": avg_rating if avg_rating is not None else 0.0}
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania średniej oceny: {str(e)}")


def get_movie_rating_count(movie_id):
    try:
        count = rating_repo.get_movie_rating_count(movie_id)
        return {"rating_count": count}
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania liczby ocen: {str(e)}")


def get_movie_rating_stats(movie_id):
    try:
        stats = rating_repo.get_movie_rating_stats(movie_id)
        return stats
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania statystyk ocen: {str(e)}")


def create_rating(user_id, movie_id, rating_value):
    try:
        if not (1 <= rating_value <= 10):
            raise ValueError("Ocena musi być w zakresie od 1 do 10")

        user, movie = db.session.get(User, user_id), db.session.get(Movie, movie_id)
        if not user or not movie:
            raise ValueError("Użytkownik lub film nie istnieje")

        try:
            from app.repositories.watchlist_repository import WatchlistRepository

            watchlist_repo = WatchlistRepository(db.session)
            if watchlist_repo.is_in_watchlist(user_id, movie_id):
                watchlist_repo.remove_from_watchlist(user_id, movie_id)
                print(
                    f"Film {movie_id} został automatycznie usunięty z listy do obejrzenia użytkownika {user_id} po ocenieniu"
                )
        except Exception as e:
            print(f"Błąd podczas usuwania z watchlisty: {str(e)}")

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
    try:
        if not (1 <= new_rating_value <= 10):
            raise ValueError("Ocena musi być w zakresie od 1 do 10")

        rating = rating_repo.get_by_id(rating_id)
        if not rating:
            raise ValueError("Ocena nie istnieje")

        if rating.user_id != user_id:
            raise ValueError("Nie masz uprawnień do edycji tej oceny")

        try:
            from app.repositories.watchlist_repository import WatchlistRepository

            watchlist_repo = WatchlistRepository(db.session)
            if watchlist_repo.is_in_watchlist(user_id, rating.movie_id):
                watchlist_repo.remove_from_watchlist(user_id, rating.movie_id)
                print(
                    f"Film {rating.movie_id} został automatycznie usunięty z listy do obejrzenia użytkownika {user_id} po aktualizacji oceny"
                )
        except Exception as e:
            print(f"Błąd podczas usuwania z watchlisty: {str(e)}")

        updated_rating = rating_repo.update(rating_id, new_rating_value)
        result = updated_rating.serialize()
        stats = get_movie_rating_stats(updated_rating.movie_id)
        result.update(stats)
        return result
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji oceny: {str(e)}")


def delete_rating(user_id, movie_id):
    try:
        rating = rating_repo.get_by_user_and_movie(user_id, movie_id)

        if not rating:
            return None

        if rating.user_id != user_id:
            raise ValueError("Nie masz uprawnień do usunięcia tej oceny")

        success = rating_repo.delete_movie_rating(user_id, movie_id)

        result = {"success": success, "movie_id": movie_id}

        if success:
            stats = get_movie_rating_stats(movie_id)
            result.update(stats)

        return result
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Błąd podczas usuwania oceny: {str(e)}")
