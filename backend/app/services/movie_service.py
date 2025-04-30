from app.repositories.movie_repository import MovieRepository
from app.services.database import db
from app.models.movie import Movie


movie_repo = MovieRepository(db.session)


<<<<<<< Updated upstream
def get_all_movies():
    try:
        movies = movie_repo.get_all()
        return [
            movie.serialize(include_genres=True, include_actors=True)
            for movie in movies
        ]
=======
@lru_cache(maxsize=1)
def get_filter_options_cached():
    return movie_repo.get_filter_options()


def get_all_movies(user_id=None):
    try:
        movies = movie_repo.get_all()
        if user_id:
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
        return movies  # <-- lista obiektów Movie
>>>>>>> Stashed changes
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmów: {str(e)}")


def get_movies_paginated(page=1, per_page=10, genre_id=None):
    try:
<<<<<<< Updated upstream
        result = movie_repo.get_paginated(page, per_page, genre_id)

        serialized_movies = [
            movie.serialize(include_genres=True, include_actors=True)
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
=======
        result = movie_repo.get_paginated(page, per_page, genre_id, user_id)
        movies = result["movies"]
        if user_id:
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
        return {"movies": movies, "pagination": result["pagination"]}
>>>>>>> Stashed changes
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmów z paginacją: {str(e)}")


def get_movie_by_id(movie_id, include_actors_roles=False):
    try:
        movie = movie_repo.get_by_id(movie_id)
        if not movie:
            return None
<<<<<<< Updated upstream
        return movie.serialize(
            include_genres=True,
            include_actors=True,
            include_actors_roles=include_actors_roles,
            include_directors=True,
        )
=======
        # Ustaw user_rating jeśli trzeba (np. przez repo)
        return movie
>>>>>>> Stashed changes
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmu o ID {movie_id}: {str(e)}")


<<<<<<< Updated upstream
=======
def get_top_rated_movies(limit=10, user_id=None):
    try:
        movies = movie_repo.get_top_rated(limit, user_id)
        if user_id:
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
        return movies
    except Exception as e:
        logger.error(f"Error in get_top_rated_movies: {str(e)}")
        raise Exception(f"Błąd podczas pobierania top filmów: {str(e)}")


>>>>>>> Stashed changes
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
        return new_movie  # <-- zwracaj obiekt Movie
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
        movies = result["movies"]
        if user_id:
            movie_ids = [movie.movie_id for movie in movies]
            from app.models.rating import Rating

<<<<<<< Updated upstream
        serialized_movies = [
            movie.serialize(include_genres=True, include_actors=include_actors)
            for movie in result["movies"]
        ]

        return {"movies": serialized_movies, "pagination": result["pagination"]}
=======
            user_ratings = (
                db.session.query(Rating.movie_id, Rating.rating)
                .filter(Rating.user_id == user_id, Rating.movie_id.in_(movie_ids))
                .all()
            )
            ratings_map = {movie_id: rating for movie_id, rating in user_ratings}
            for movie in movies:
                movie._user_rating = ratings_map.get(movie.movie_id)
        return {"movies": movies, "pagination": result["pagination"]}
>>>>>>> Stashed changes
    except Exception as e:
        raise Exception(f"Błąd podczas filtrowania filmów: {str(e)}")


def get_movie_filter_options():
    try:
        return movie_repo.get_filter_options()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania opcji filtrów: {str(e)}")
<<<<<<< Updated upstream
=======


def search_movies(query, page=1, per_page=10, user_id=None):
    try:
        result = movie_repo.search(
            query=query,
            page=page,
            per_page=per_page,
            user_id=user_id,
        )
        movies = result["movies"]
        if user_id:
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
        return {"movies": movies, "pagination": result["pagination"]}
    except Exception as e:
        logger.error(f"Error in search_movies: {str(e)}")
        raise Exception(f"Błąd podczas wyszukiwania filmów: {str(e)}")
>>>>>>> Stashed changes
