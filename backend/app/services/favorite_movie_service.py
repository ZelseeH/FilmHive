from app.repositories.favorite_movie_repository import FavoriteMovieRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app.models.movie import Movie
from app.models.user import User


class FavoriteMovieService:
    def __init__(self):
        self.favorite_repository = FavoriteMovieRepository(db.session)

    def add_to_favorites(self, user_id, movie_id):
        """Dodaje film do ulubionych użytkownika."""
        try:
            # Sprawdź, czy użytkownik i film istnieją
            user = db.session.get(User, user_id)
            movie = db.session.get(Movie, movie_id)

            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            # Sprawdź, czy film już jest w ulubionych
            if self.favorite_repository.is_favorite(user_id, movie_id):
                current_app.logger.info(
                    f"Film {movie_id} już jest w ulubionych użytkownika {user_id}"
                )
                favorite = self.favorite_repository.get_user_favorites(user_id)[0]
                return favorite.serialize()

            favorite = self.favorite_repository.add_favorite(user_id, movie_id)
            current_app.logger.info(
                f"Dodano film {movie_id} do ulubionych użytkownika {user_id}"
            )
            return favorite.serialize()
        except ValueError as e:
            current_app.logger.error(f"ValueError adding to favorites: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError adding to favorites: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się dodać filmu do ulubionych: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error adding to favorites: {str(e)}")
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def remove_from_favorites(self, user_id, movie_id):
        """Usuwa film z ulubionych użytkownika."""
        try:
            # Sprawdź, czy użytkownik istnieje
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            success = self.favorite_repository.remove_favorite(user_id, movie_id)
            if success:
                current_app.logger.info(
                    f"Usunięto film {movie_id} z ulubionych użytkownika {user_id}"
                )
            else:
                current_app.logger.info(
                    f"Film {movie_id} nie był w ulubionych użytkownika {user_id}"
                )

            return {"success": success}
        except ValueError as e:
            current_app.logger.error(f"ValueError removing from favorites: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError removing from favorites: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Nie udało się usunąć filmu z ulubionych: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error removing from favorites: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def check_if_favorite(self, user_id, movie_id):
        """Sprawdza, czy film jest w ulubionych użytkownika."""
        try:
            # Sprawdź, czy użytkownik istnieje
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            is_favorite = self.favorite_repository.is_favorite(user_id, movie_id)
            current_app.logger.info(
                f"Sprawdzono, czy film {movie_id} jest w ulubionych użytkownika {user_id}: {is_favorite}"
            )
            return {"is_favorite": is_favorite}
        except ValueError as e:
            current_app.logger.error(f"ValueError checking favorite status: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError checking favorite status: {str(e)}"
            )
            raise Exception(f"Nie udało się sprawdzić statusu ulubionego: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error checking favorite status: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_user_favorites(self, user_id):
        """Pobiera wszystkie ulubione filmy użytkownika."""
        try:
            # Sprawdź, czy użytkownik istnieje
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            favorites = self.favorite_repository.get_user_favorites(user_id)
            current_app.logger.info(
                f"Pobrano {len(favorites)} ulubionych filmów użytkownika {user_id}"
            )
            return [favorite.serialize() for favorite in favorites]
        except ValueError as e:
            current_app.logger.error(f"ValueError getting user favorites: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting user favorites: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać ulubionych filmów: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting user favorites: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_user_favorite_movies(self, user_id, page=1, per_page=10):
        """Pobiera ulubione filmy użytkownika z paginacją."""
        try:
            # Sprawdź, czy użytkownik istnieje
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            # Walidacja parametrów paginacji
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 50:
                per_page = 50

            result = self.favorite_repository.get_user_favorite_movies(
                user_id, page, per_page
            )
            current_app.logger.info(
                f"Pobrano ulubione filmy użytkownika {user_id}, strona {page}, {len(result['movies'])} filmów"
            )
            return result
        except ValueError as e:
            current_app.logger.error(
                f"ValueError getting user favorite movies: {str(e)}"
            )
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting user favorite movies: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać ulubionych filmów: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting user favorite movies: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_movie_favorite_count(self, movie_id):
        """Pobiera liczbę użytkowników, którzy dodali film do ulubionych."""
        try:
            # Sprawdź, czy film istnieje
            movie = db.session.get(Movie, movie_id)
            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            count = self.favorite_repository.get_movie_favorite_count(movie_id)
            current_app.logger.info(f"Film {movie_id} ma {count} polubień")
            return count
        except ValueError as e:
            current_app.logger.error(
                f"ValueError getting movie favorite count: {str(e)}"
            )
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting movie favorite count: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać liczby polubień: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting movie favorite count: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")
