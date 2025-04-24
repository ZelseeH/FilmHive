from app.repositories.watchlist_repository import WatchlistRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app.models.movie import Movie
from app.models.user import User


class WatchlistService:
    def __init__(self):
        self.watchlist_repository = WatchlistRepository(db.session)

    def add_to_watchlist(self, user_id, movie_id):
        try:
            user = db.session.get(User, user_id)
            movie = db.session.get(Movie, movie_id)

            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            if self.watchlist_repository.is_in_watchlist(user_id, movie_id):
                current_app.logger.info(
                    f"Film {movie_id} już jest na liście do obejrzenia użytkownika {user_id}"
                )
                watchlist_entries = self.watchlist_repository.get_user_watchlist(
                    user_id
                )
                if watchlist_entries and len(watchlist_entries) > 0:
                    watchlist_entry = watchlist_entries[0]
                    return watchlist_entry.serialize()
                else:
                    return {"message": "Film już jest na liście do obejrzenia"}

            watchlist_entry = self.watchlist_repository.add_to_watchlist(
                user_id, movie_id
            )
            current_app.logger.info(
                f"Dodano film {movie_id} do listy do obejrzenia użytkownika {user_id}"
            )
            return watchlist_entry.serialize()
        except ValueError as e:
            current_app.logger.error(f"ValueError adding to watchlist: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError adding to watchlist: {str(e)}")
            db.session.rollback()
            raise Exception(
                f"Nie udało się dodać filmu do listy do obejrzenia: {str(e)}"
            )
        except Exception as e:
            current_app.logger.error(f"Unexpected error adding to watchlist: {str(e)}")
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def remove_from_watchlist(self, user_id, movie_id):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            success = self.watchlist_repository.remove_from_watchlist(user_id, movie_id)
            if success:
                current_app.logger.info(
                    f"Usunięto film {movie_id} z listy do obejrzenia użytkownika {user_id}"
                )
            else:
                current_app.logger.info(
                    f"Film {movie_id} nie był na liście do obejrzenia użytkownika {user_id}"
                )

            return {"success": success}
        except ValueError as e:
            current_app.logger.error(f"ValueError removing from watchlist: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError removing from watchlist: {str(e)}"
            )
            db.session.rollback()
            raise Exception(
                f"Nie udało się usunąć filmu z listy do obejrzenia: {str(e)}"
            )
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error removing from watchlist: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def check_if_in_watchlist(self, user_id, movie_id):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            is_in_watchlist = self.watchlist_repository.is_in_watchlist(
                user_id, movie_id
            )
            current_app.logger.info(
                f"Sprawdzono, czy film {movie_id} jest na liście do obejrzenia użytkownika {user_id}: {is_in_watchlist}"
            )
            return {"is_in_watchlist": is_in_watchlist}
        except ValueError as e:
            current_app.logger.error(f"ValueError checking watchlist status: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError checking watchlist status: {str(e)}"
            )
            raise Exception(
                f"Nie udało się sprawdzić statusu listy do obejrzenia: {str(e)}"
            )
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error checking watchlist status: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_user_watchlist(self, user_id, page=1, per_page=10):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 50:
                per_page = 50

            result = self.watchlist_repository.get_user_watchlist_movies(
                user_id, page, per_page
            )
            current_app.logger.info(
                f"Pobrano filmy z listy do obejrzenia użytkownika {user_id}, strona {page}, {len(result['movies'])} filmów"
            )
            return result
        except ValueError as e:
            current_app.logger.error(f"ValueError getting user watchlist: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting user watchlist: {str(e)}"
            )
            raise Exception(
                f"Nie udało się pobrać filmów z listy do obejrzenia: {str(e)}"
            )
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting user watchlist: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_recent_watchlist_movies(self, user_id, limit=6):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            movies = self.watchlist_repository.get_recent_watchlist_movies(
                user_id, limit
            )
            current_app.logger.info(
                f"Pobrano ostatnie {len(movies)} filmy z listy do obejrzenia użytkownika {user_id}"
            )
            return {"movies": movies}
        except ValueError as e:
            current_app.logger.error(
                f"ValueError getting recent watchlist movies: {str(e)}"
            )
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting recent watchlist movies: {str(e)}"
            )
            raise Exception(
                f"Nie udało się pobrać ostatnich filmów z listy do obejrzenia: {str(e)}"
            )
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting recent watchlist movies: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")
