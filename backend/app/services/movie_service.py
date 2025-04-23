from app.repositories.movie_repository import MovieRepository
from app.services.database import db
from app.models.movie import Movie
from sqlalchemy import desc


movie_repo = MovieRepository(db.session)


def get_all_movies():
    try:
        movies = movie_repo.get_all()
        return [
            movie.serialize(include_genres=True, include_actors=True)
            for movie in movies
        ]
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmów: {str(e)}")


def get_movies_paginated(page=1, per_page=10, genre_id=None):
    try:
        result = movie_repo.get_paginated(page, per_page, genre_id)

        serialized_movies = [
            movie.serialize(include_genres=True, include_actors=True)
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmów z paginacją: {str(e)}")


def get_movie_by_id(movie_id, include_actors_roles=False):
    try:
        movie = movie_repo.get_by_id(movie_id)
        if not movie:
            return None
        return movie.serialize(
            include_genres=True,
            include_actors=True,
            include_actors_roles=include_actors_roles,
            include_directors=True,
        )
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmu o ID {movie_id}: {str(e)}")


def get_top_rated_movies(limit=10):
    try:
        movies = movie_repo.get_top_rated(limit)
        return [
            movie.serialize(include_genres=True, include_actors=True)
            for movie in movies
        ]
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania top filmów: {str(e)}")


def create_movie(data):
    try:
        new_movie = Movie(
            title=data.get("title"),
            release_date=data.get("release_date"),
            description=data.get("description", ""),
            poster_url=data.get("poster_url", ""),
            duration_minutes=data.get("duration_minutes", 0),
            country=data.get("country", ""),
            original_language=data.get("original_language", ""),
        )
        movie_repo.add(new_movie)
        return new_movie.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas tworzenia filmu: {str(e)}")


def delete_movie(movie_id):
    try:
        success = movie_repo.delete(movie_id)
        return success
    except Exception as e:
        raise Exception(f"Błąd podczas usuwania filmu o ID {movie_id}: {str(e)}")


def filter_movies(
    filters,
    page=1,
    per_page=10,
    include_actors=False,
    sort_by="title",
    sort_order="asc",
):
    try:
        result = movie_repo.filter_movies(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        serialized_movies = [
            movie.serialize(include_genres=True, include_actors=include_actors)
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
    except Exception as e:
        raise Exception(f"Błąd podczas filtrowania filmów: {str(e)}")


def get_movie_filter_options():
    try:
        return movie_repo.get_filter_options()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania opcji filtrów: {str(e)}")
