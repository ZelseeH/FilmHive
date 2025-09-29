from app.models.watchlist import Watchlist
from app.models.movie import Movie
from app.models.user import User
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from flask import url_for
import logging


class WatchlistRepository:
    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def _check_user_movie_exist(self, user_id, movie_id):
        user = self.session.get(User, user_id)
        if not user:
            self.logger.error(f"Użytkownik o ID {user_id} nie istnieje")
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

        movie = self.session.get(Movie, movie_id)
        if not movie:
            self.logger.error(f"Film o ID {movie_id} nie istnieje")
            raise ValueError(f"Film o ID {movie_id} nie istnieje")

        return user, movie

    def add_to_watchlist(self, user_id, movie_id):
        try:
            self._check_user_movie_exist(user_id, movie_id)

            existing = (
                self.session.query(Watchlist)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if existing:
                self.logger.info(
                    f"Film {movie_id} już jest na liście do obejrzenia użytkownika {user_id}"
                )
                return existing

            watchlist_entry = Watchlist(user_id=user_id, movie_id=movie_id)
            self.session.add(watchlist_entry)
            self.session.commit()
            self.logger.info(
                f"Dodano film {movie_id} do listy do obejrzenia użytkownika {user_id}"
            )
            return watchlist_entry
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Błąd podczas dodawania do listy do obejrzenia: {str(e)}"
            )
            raise

    def remove_from_watchlist(self, user_id, movie_id):
        try:
            self._check_user_movie_exist(user_id, movie_id)

            watchlist_entry = (
                self.session.query(Watchlist)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if watchlist_entry:
                self.session.delete(watchlist_entry)
                self.session.commit()
                self.logger.info(
                    f"Usunięto film {movie_id} z listy do obejrzenia użytkownika {user_id}"
                )
                return True

            self.logger.info(
                f"Film {movie_id} nie był na liście do obejrzenia użytkownika {user_id}"
            )
            return False
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Błąd podczas usuwania z listy do obejrzenia: {str(e)}")
            raise

    def is_in_watchlist(self, user_id, movie_id):
        try:
            result = (
                self.session.query(Watchlist)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
                is not None
            )
            self.logger.info(
                f"Sprawdzenie czy film {movie_id} jest na liście do obejrzenia użytkownika {user_id}: {result}"
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Błąd podczas sprawdzania statusu listy do obejrzenia: {str(e)}"
            )
            raise

    def get_user_watchlist(self, user_id):
        try:
            watchlist = self.session.query(Watchlist).filter_by(user_id=user_id).all()
            self.logger.info(
                f"Pobrano {len(watchlist)} filmów z listy do obejrzenia użytkownika {user_id}"
            )
            return watchlist
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania listy do obejrzenia: {str(e)}")
            raise

    def get_user_watchlist_movies(self, user_id, page=1, per_page=10):
        try:
            query = (
                self.session.query(Movie)
                .join(Watchlist, Movie.movie_id == Watchlist.movie_id)
                .filter(Watchlist.user_id == user_id)
            )

            if hasattr(Movie, "genres"):
                query = query.options(joinedload(Movie.genres))

            total = query.count()
            movies = query.limit(per_page).offset((page - 1) * per_page).all()
            total_pages = (total + per_page - 1) // per_page

            self.logger.info(
                f"Pobrano {len(movies)} z {total} filmów z listy do obejrzenia użytkownika {user_id} (strona {page}/{total_pages})"
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
        except Exception as e:
            self.logger.error(
                f"Błąd podczas pobierania filmów z listy do obejrzenia: {str(e)}"
            )
            raise

    def get_recent_watchlist_movies(self, user_id, limit=6):
        try:
            results = (
                self.session.query(Watchlist, Movie)
                .join(Movie, Watchlist.movie_id == Movie.movie_id)
                .filter(Watchlist.user_id == user_id)
                .order_by(Watchlist.added_at.desc())
                .limit(limit)
                .all()
            )

            self.logger.info(
                f"Pobrano {len(results)} ostatnich filmów z listy do obejrzenia użytkownika {user_id}"
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
                    "added_at": (
                        watchlist.added_at.isoformat() if watchlist.added_at else None
                    ),
                }
                for watchlist, movie in results
            ]
        except Exception as e:
            self.logger.error(
                f"Błąd podczas pobierania ostatnich filmów z listy do obejrzenia: {str(e)}"
            )
            raise

    # 🆕 NOWA METODA - Wszystkie filmy z watchlisty
    def get_all_watchlist_movies(self, user_id):
        """Pobierz wszystkie filmy z listy do obejrzenia użytkownika (bez limitu)"""
        try:
            results = (
                self.session.query(Watchlist, Movie)
                .join(Movie, Watchlist.movie_id == Movie.movie_id)
                .filter(Watchlist.user_id == user_id)
                .order_by(Watchlist.added_at.desc())
                .all()
            )

            self.logger.info(
                f"Pobrano wszystkie {len(results)} filmów z listy do obejrzenia użytkownika {user_id}"
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
                    "added_at": (
                        watchlist.added_at.isoformat() if watchlist.added_at else None
                    ),
                }
                for watchlist, movie in results
            ]
        except Exception as e:
            self.logger.error(
                f"Błąd podczas pobierania wszystkich filmów z listy do obejrzenia: {str(e)}"
            )
            raise
