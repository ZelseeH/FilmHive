# app/repositories/favorite_movie_repository.py
from app.models.favorite_movie import FavoriteMovie
from app.models.movie import Movie
from app.models.user import User
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from flask import url_for
import logging


class FavoriteMovieRepository:
    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def add_favorite(self, user_id, movie_id):
        try:
            # Sprawdź czy użytkownik istnieje
            user = self.session.get(User, user_id)
            if not user:
                self.logger.error(f"Użytkownik o ID {user_id} nie istnieje")
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            # Sprawdź czy film istnieje
            movie = self.session.get(Movie, movie_id)
            if not movie:
                self.logger.error(f"Film o ID {movie_id} nie istnieje")
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            existing = (
                self.session.query(FavoriteMovie)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if existing:
                self.logger.info(
                    f"Film {movie_id} już jest w ulubionych użytkownika {user_id}"
                )
                return existing

            favorite = FavoriteMovie(user_id=user_id, movie_id=movie_id)
            self.session.add(favorite)
            self.session.commit()
            self.logger.info(
                f"Dodano film {movie_id} do ulubionych użytkownika {user_id}"
            )
            return favorite
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Błąd SQL podczas dodawania do ulubionych: {str(e)}")
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Nieoczekiwany błąd podczas dodawania do ulubionych: {str(e)}"
            )
            raise

    def remove_favorite(self, user_id, movie_id):
        try:
            # Sprawdź czy użytkownik istnieje
            user = self.session.get(User, user_id)
            if not user:
                self.logger.error(f"Użytkownik o ID {user_id} nie istnieje")
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            # Sprawdź czy film istnieje
            movie = self.session.get(Movie, movie_id)
            if not movie:
                self.logger.error(f"Film o ID {movie_id} nie istnieje")
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            favorite = (
                self.session.query(FavoriteMovie)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if favorite:
                self.session.delete(favorite)
                self.session.commit()
                self.logger.info(
                    f"Usunięto film {movie_id} z ulubionych użytkownika {user_id}"
                )
                return True

            self.logger.info(
                f"Film {movie_id} nie był w ulubionych użytkownika {user_id}"
            )
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Błąd SQL podczas usuwania z ulubionych: {str(e)}")
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Nieoczekiwany błąd podczas usuwania z ulubionych: {str(e)}"
            )
            raise

    def is_favorite(self, user_id, movie_id):
        try:
            result = (
                self.session.query(FavoriteMovie)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
                is not None
            )
            self.logger.info(
                f"Sprawdzenie czy film {movie_id} jest w ulubionych użytkownika {user_id}: {result}"
            )
            return result
        except SQLAlchemyError as e:
            self.logger.error(
                f"Błąd SQL podczas sprawdzania statusu ulubionego: {str(e)}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Nieoczekiwany błąd podczas sprawdzania statusu ulubionego: {str(e)}"
            )
            raise

    def get_user_favorites(self, user_id):
        try:
            favorites = (
                self.session.query(FavoriteMovie).filter_by(user_id=user_id).all()
            )
            self.logger.info(
                f"Pobrano {len(favorites)} ulubionych filmów użytkownika {user_id}"
            )
            return favorites
        except SQLAlchemyError as e:
            self.logger.error(f"Błąd SQL podczas pobierania ulubionych: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(
                f"Nieoczekiwany błąd podczas pobierania ulubionych: {str(e)}"
            )
            raise

    def get_user_favorite_movies(self, user_id, page=1, per_page=10):
        try:
            query = (
                self.session.query(Movie)
                .join(FavoriteMovie, Movie.movie_id == FavoriteMovie.movie_id)
                .filter(FavoriteMovie.user_id == user_id)
            )

            if hasattr(Movie, "genres"):
                query = query.options(joinedload(Movie.genres))

            total = query.count()
            movies = query.limit(per_page).offset((page - 1) * per_page).all()

            total_pages = (total + per_page - 1) // per_page

            self.logger.info(
                f"Pobrano {len(movies)} z {total} ulubionych filmów użytkownika {user_id} (strona {page}/{total_pages})"
            )

            return {
                "movies": [movie.serialize() for movie in movies],
                "pagination": {
                    "total": total,
                    "total_pages": total_pages,
                    "page": page,
                    "per_page": per_page,
                },
            }
        except SQLAlchemyError as e:
            self.logger.error(
                f"Błąd SQL podczas pobierania ulubionych filmów: {str(e)}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Nieoczekiwany błąd podczas pobierania ulubionych filmów: {str(e)}"
            )
            raise

    def get_movie_favorite_count(self, movie_id):
        try:
            count = (
                self.session.query(FavoriteMovie).filter_by(movie_id=movie_id).count()
            )
            self.logger.info(f"Film {movie_id} ma {count} polubień")
            return count
        except SQLAlchemyError as e:
            self.logger.error(f"Błąd SQL podczas pobierania liczby polubień: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(
                f"Nieoczekiwany błąd podczas pobierania liczby polubień: {str(e)}"
            )
            raise

    def get_recent_favorite_movies(self, user_id, limit=6):
        try:
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
                            "static",
                            filename=f"posters/{movie.poster_url}",
                            _external=True,
                        )
                        if movie.poster_url
                        else None
                    ),
                    "added_at": fav.added_at.isoformat() if fav.added_at else None,
                }
                for fav, movie in results
            ]
        except SQLAlchemyError as e:
            self.logger.error(
                f"Błąd SQL podczas pobierania ostatnich ulubionych filmów: {str(e)}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Nieoczekiwany błąd podczas pobierania ostatnich ulubionych filmów: {str(e)}"
            )
            raise

    def get_all_favorite_movies(self, user_id):
        """Pobierz wszystkie ulubione filmy użytkownika (bez limitu)"""
        try:
            results = (
                self.session.query(FavoriteMovie, Movie)
                .join(Movie, FavoriteMovie.movie_id == Movie.movie_id)
                .filter(FavoriteMovie.user_id == user_id)
                .order_by(FavoriteMovie.added_at.desc())
                .all()
            )

            self.logger.info(
                f"Pobrano wszystkie {len(results)} ulubione filmy użytkownika {user_id}"
            )

            return [
                {
                    "movie_id": movie.movie_id,
                    "title": movie.title,
                    "poster_url": (
                        url_for(
                            "static",
                            filename=f"posters/{movie.poster_url}",
                            _external=True,
                        )
                        if movie.poster_url
                        else None
                    ),
                    "added_at": fav.added_at.isoformat() if fav.added_at else None,
                }
                for fav, movie in results
            ]
        except SQLAlchemyError as e:
            self.logger.error(
                f"Błąd SQL podczas pobierania wszystkich ulubionych filmów: {str(e)}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Nieoczekiwany błąd podczas pobierania wszystkich ulubionych filmów: {str(e)}"
            )
            raise
