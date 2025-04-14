from app.models.watchlist import Watchlist
from app.models.movie import Movie
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError


class WatchlistRepository:
    def __init__(self, session):
        self.session = session

    def add_to_watchlist(self, user_id, movie_id):
        try:
            existing = (
                self.session.query(Watchlist)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if existing:
                print(
                    f"Film {movie_id} już jest na liście do obejrzenia użytkownika {user_id}"
                )
                return existing

            watchlist_entry = Watchlist(user_id=user_id, movie_id=movie_id)
            self.session.add(watchlist_entry)
            self.session.commit()
            print(
                f"Dodano film {movie_id} do listy do obejrzenia użytkownika {user_id}"
            )
            return watchlist_entry
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas dodawania do listy do obejrzenia: {e}")
            raise

    def remove_from_watchlist(self, user_id, movie_id):
        try:
            watchlist_entry = (
                self.session.query(Watchlist)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if watchlist_entry:
                self.session.delete(watchlist_entry)
                self.session.commit()
                print(
                    f"Usunięto film {movie_id} z listy do obejrzenia użytkownika {user_id}"
                )
                return True
            print(
                f"Film {movie_id} nie był na liście do obejrzenia użytkownika {user_id}"
            )
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania z listy do obejrzenia: {e}")
            raise

    def is_in_watchlist(self, user_id, movie_id):
        try:
            result = (
                self.session.query(Watchlist)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
                is not None
            )
            print(
                f"Sprawdzenie czy film {movie_id} jest na liście do obejrzenia użytkownika {user_id}: {result}"
            )
            return result
        except SQLAlchemyError as e:
            print(f"Błąd podczas sprawdzania statusu listy do obejrzenia: {e}")
            raise

    def get_user_watchlist(self, user_id):
        try:
            watchlist = self.session.query(Watchlist).filter_by(user_id=user_id).all()
            print(
                f"Pobrano {len(watchlist)} filmów z listy do obejrzenia użytkownika {user_id}"
            )
            return watchlist
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania listy do obejrzenia: {e}")
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

            print(
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
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania filmów z listy do obejrzenia: {e}")
            raise
        except Exception as e:
            print(
                f"Nieoczekiwany błąd podczas pobierania filmów z listy do obejrzenia: {e}"
            )
            raise
