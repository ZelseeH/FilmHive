from app.repositories.movie_repository import MovieRepository
from app.services.database import db
from app.models.movie import Movie
from sqlalchemy import desc
from functools import lru_cache
import logging
from datetime import date
from datetime import datetime

logger = logging.getLogger(__name__)
movie_repo = MovieRepository(db.session)


@lru_cache(maxsize=1)
def get_filter_options_cached():
    return movie_repo.get_filter_options()


def get_all_movies(serialize_basic=False, user_id=None):
    """✅ POPRAWIONE - pobiera WSZYSTKIE filmy bez filtrowania dat"""
    try:
        movies = movie_repo.get_all()

        if user_id:
            # Pobierz oceny użytkownika dla filmów
            movie_ids = [movie.movie_id for movie in movies]
            from app.models.rating import Rating

            user_ratings = (
                db.session.query(Rating.movie_id, Rating.rating)
                .filter(Rating.user_id == user_id, Rating.movie_id.in_(movie_ids))
                .all()
            )

            ratings_map = {movie_id: rating for movie_id, rating in user_ratings}
            for movie in movies:
                movie._user_rating = ratings_map.get(movie.movie_id)

        if serialize_basic:
            return [movie.serialize_basic() for movie in movies]

        return [
            {
                **movie.serialize(include_genres=True),
                "user_rating": getattr(movie, "_user_rating", None),
            }
            for movie in movies
        ]
    except Exception as e:
        logger.error(f"Error in get_all_movies: {str(e)}")
        raise Exception(f"Błąd podczas pobierania filmów: {str(e)}")


def get_movies_paginated(page=1, per_page=10, genre_id=None, user_id=None):
    """✅ POPRAWIONE - pobiera WSZYSTKIE filmy z paginacją"""
    try:
        result = movie_repo.get_paginated(page, per_page, genre_id, user_id)

        serialized_movies = [
            {
                **movie.serialize(include_genres=True),
                "user_rating": getattr(movie, "_user_rating", None),
            }
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
    except Exception as e:
        logger.error(f"Error in get_movies_paginated: {str(e)}")
        raise Exception(f"Błąd podczas pobierania filmów z paginacją: {str(e)}")


def get_movie_by_id(movie_id, include_actors_roles=False, user_id=None):
    """Pobiera pojedynczy film - bez względu na datę premiery"""
    try:
        movie = movie_repo.get_by_id(movie_id, user_id)
        if not movie:
            return None

        return {
            **movie.serialize(
                include_genres=True,
                include_actors=True,
                include_actors_roles=include_actors_roles,
                include_directors=True,
            ),
            "user_rating": getattr(movie, "_user_rating", None),
        }
    except Exception as e:
        logger.error(f"Error in get_movie_by_id: {str(e)}")
        raise Exception(f"Błąd podczas pobierania filmu o ID {movie_id}: {str(e)}")


def get_top_rated_movies(limit=10, user_id=None):
    """✅ POPRAWIONE - najlepiej oceniane WSZYSTKIE filmy"""
    try:
        movies = movie_repo.get_top_rated(limit, user_id)

        for movie in movies:
            logger.debug(
                f"Movie: {movie.title}, Rating count: {movie._rating_count}, Avg rating: {movie._average_rating}"
            )

        return [
            {
                **movie.serialize(include_genres=True),
                "user_rating": getattr(movie, "_user_rating", None),
            }
            for movie in movies
        ]
    except Exception as e:
        logger.error(f"Error in get_top_rated_movies: {str(e)}")
        raise Exception(f"Błąd podczas pobierania top filmów: {str(e)}")


def create_movie(data):
    """✅ POPRAWIONE - tworzy film bez ograniczenia dat premiery"""
    try:
        new_movie = Movie(
            title=data.get("title"),
            release_date=data.get("release_date"),  # ✅ Przyszłe daty dozwolone
            description=data.get("description", ""),
            poster_url=data.get("poster_url", ""),
            duration_minutes=data.get("duration_minutes", 0),
            country=data.get("country", ""),
            original_language=data.get("original_language", ""),
            trailer_url=data.get("trailer_url", ""),
        )
        movie_repo.add(new_movie)
        return new_movie.serialize()
    except Exception as e:
        logger.error(f"Error in create_movie: {str(e)}")
        raise Exception(f"Błąd podczas tworzenia filmu: {str(e)}")


def delete_movie(movie_id):
    """Usuwa film - bez względu na datę premiery"""
    try:
        success = movie_repo.delete(movie_id)
        return success
    except Exception as e:
        logger.error(f"Error in delete_movie: {str(e)}")
        raise Exception(f"Błąd podczas usuwania filmu o ID {movie_id}: {str(e)}")


def filter_movies(
    filters,
    page=1,
    per_page=10,
    include_actors=False,
    sort_by="title",
    sort_order="asc",
    user_id=None,
):
    """✅ POPRAWIONE - filtruje WSZYSTKIE filmy bez ograniczenia dat"""
    try:
        result = movie_repo.filter_movies(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            user_id=user_id,
        )

        serialized_movies = [
            {
                **movie.serialize(include_genres=True, include_actors=include_actors),
                "user_rating": getattr(movie, "_user_rating", None),
            }
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
    except Exception as e:
        logger.error(f"Error in filter_movies: {str(e)}")
        raise Exception(f"Błąd podczas filtrowania filmów: {str(e)}")


def get_movie_filter_options():
    """✅ POPRAWIONE - opcje filtrów dla WSZYSTKICH filmów"""
    try:
        return get_filter_options_cached()
    except Exception as e:
        logger.error(f"Error in get_movie_filter_options: {str(e)}")
        raise Exception(f"Błąd podczas pobierania opcji filtrów: {str(e)}")


def search_movies(query, page=1, per_page=10, user_id=None):
    """✅ POPRAWIONE - wyszukuje WSZYSTKIE filmy"""
    try:
        result = movie_repo.search(
            query=query,
            page=page,
            per_page=per_page,
            user_id=user_id,
        )
        serialized_movies = [
            {
                **movie.serialize(include_genres=True, include_actors=True),
                "user_rating": getattr(movie, "_user_rating", None),
            }
            for movie in result["movies"]
        ]
        return {"movies": serialized_movies, "pagination": result["pagination"]}
    except Exception as e:
        logger.error(f"Error in search_movies: {str(e)}")
        raise Exception(f"Błąd podczas wyszukiwania filmów: {str(e)}")


def get_all_movies_with_title_filter(title_filter=None, page=1, per_page=10):
    """✅ POPRAWIONE - pobiera WSZYSTKIE filmy z filtrem tytułu"""
    try:
        result = movie_repo.get_all_with_title_filter(
            title_filter=title_filter, page=page, per_page=per_page
        )

        serialized_movies = [
            movie.serialize(
                include_genres=True, include_actors=True, include_directors=True
            )
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
    except Exception as e:
        logger.error(f"Error in get_all_movies_with_title_filter: {str(e)}")
        raise Exception(f"Błąd podczas pobierania filmów z filtrowaniem: {str(e)}")


def update_movie(movie_id, data):
    """✅ POPRAWIONE - aktualizuje film bez ograniczenia dat premiery"""
    try:
        updated_movie = movie_repo.update(movie_id, data)
        if not updated_movie:
            return None

        return updated_movie.serialize(
            include_genres=True, include_actors=True, include_directors=True
        )
    except Exception as e:
        logger.error(f"Error in update_movie: {str(e)}")
        raise Exception(f"Błąd podczas aktualizacji filmu o ID {movie_id}: {str(e)}")


def update_movie_poster(movie_id, poster_url):
    """Aktualizuje plakat filmu"""
    try:
        updated_movie = movie_repo.update_poster(movie_id, poster_url)
        if not updated_movie:
            return None

        return updated_movie.serialize(
            include_genres=True, include_actors=True, include_directors=True
        )
    except Exception as e:
        logger.error(f"Error in update_movie_poster: {str(e)}")
        raise Exception(
            f"Błąd podczas aktualizacji plakatu filmu o ID {movie_id}: {str(e)}"
        )


def get_basic_statistics():
    """✅ POPRAWIONE - statystyki WSZYSTKICH filmów"""
    try:
        stats = movie_repo.get_basic_statistics()
        return stats
    except Exception as e:
        raise Exception(f"Nie udało się pobrać statystyk: {str(e)}")


def get_dashboard_data():
    """✅ POPRAWIONE - dashboard WSZYSTKICH filmów"""
    try:
        dashboard_data = movie_repo.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise Exception(f"Nie udało się pobrać danych dashboard: {str(e)}")


def get_upcoming_movies_by_month(year, month):
    """✅ POPRAWIONE - pobiera WSZYSTKIE filmy z danego miesiąca (przeszłe i przyszłe)"""
    try:
        # Walidacja parametrów
        if not isinstance(year, int) or year < 1900 or year > 2100:
            raise ValueError("Rok musi być liczbą całkowitą między 1900 a 2100")

        if not isinstance(month, int) or month < 1 or month > 12:
            raise ValueError("Miesiąc musi być liczbą całkowitą między 1 a 12")

        # Pobierz filmy z repository (już poprawionego - wszystkie filmy)
        movies = movie_repo.get_upcoming_movies_by_month(year, month)

        # Serializuj filmy z dodaną liczbą watchlist i informacją o statusie
        today = date.today()
        serialized_movies = [
            {
                **movie.serialize(include_genres=True),
                "release_date_formatted": (
                    movie.release_date.strftime("%d.%m.%Y")
                    if movie.release_date
                    else None
                ),
                "days_until_release": (
                    (movie.release_date - today).days if movie.release_date else None
                ),
                "is_upcoming": (
                    movie.release_date > today if movie.release_date else False
                ),
                "is_released": (
                    movie.release_date <= today if movie.release_date else False
                ),
                "watchlist_count": getattr(movie, "_watchlist_count", 0),
            }
            for movie in movies
        ]

        logger.info(
            f"Pobrano {len(serialized_movies)} filmów z premierami w {month:02d}/{year}"
        )

        return {
            "movies": serialized_movies,
            "year": year,
            "month": month,
            "month_name": get_month_name(month),
            "total_count": len(serialized_movies),
            "upcoming_count": sum(1 for m in serialized_movies if m["is_upcoming"]),
            "released_count": sum(1 for m in serialized_movies if m["is_released"]),
        }

    except ValueError as e:
        logger.error(f"Błąd walidacji w get_upcoming_movies_by_month: {str(e)}")
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error in get_upcoming_movies_by_month: {str(e)}")
        raise Exception(
            f"Błąd podczas pobierania filmów z premierami dla {month:02d}/{year}: {str(e)}"
        )


def get_month_name(month):
    """Pomocnicza funkcja do zwracania nazwy miesiąca po polsku"""
    months = {
        1: "Styczeń",
        2: "Luty",
        3: "Marzec",
        4: "Kwiecień",
        5: "Maj",
        6: "Czerwiec",
        7: "Lipiec",
        8: "Sierpień",
        9: "Wrzesień",
        10: "Październik",
        11: "Listopad",
        12: "Grudzień",
    }
    return months.get(month, "Nieznany")


def get_upcoming_premieres(limit=5):
    """Pobiera nadchodzące premiery filmowe z trailerami"""
    try:
        premieres = movie_repo.get_upcoming_premieres(limit)

        # Dodatkowe przetwarzanie danych dla frontend
        processed_premieres = []
        for premiere in premieres:
            processed_premiere = {
                **premiere,
                "release_date_formatted": (
                    datetime.fromisoformat(premiere["release_date"]).strftime(
                        "%d.%m.%Y"
                    )
                    if premiere["release_date"]
                    else None
                ),
                "days_until_release": (
                    (
                        datetime.fromisoformat(premiere["release_date"]).date()
                        - date.today()
                    ).days
                    if premiere["release_date"]
                    else None
                ),
            }
            processed_premieres.append(processed_premiere)

        logger.info(
            f"Pobrano {len(processed_premieres)} nadchodzących premier z trailerami"
        )

        return processed_premieres

    except Exception as e:
        logger.error(f"Error in get_upcoming_premieres: {str(e)}")
        raise Exception(f"Błąd podczas pobierania nadchodzących premier: {str(e)}")
