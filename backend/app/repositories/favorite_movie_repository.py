from app.models.favorite_movie import FavoriteMovie
from app.models.movie import Movie
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError


class FavoriteMovieRepository:
    def __init__(self, session):
        self.session = session

    def add_favorite(self, user_id, movie_id):
        try:
            existing = (
                self.session.query(FavoriteMovie)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if existing:
                print(f"Film {movie_id} już jest w ulubionych użytkownika {user_id}")
                return existing

            favorite = FavoriteMovie(user_id=user_id, movie_id=movie_id)
            self.session.add(favorite)
            self.session.commit()
            print(f"Dodano film {movie_id} do ulubionych użytkownika {user_id}")
            return favorite
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas dodawania do ulubionych: {e}")
            raise

    def remove_favorite(self, user_id, movie_id):
        try:
            favorite = (
                self.session.query(FavoriteMovie)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
            )

            if favorite:
                self.session.delete(favorite)
                self.session.commit()
                print(f"Usunięto film {movie_id} z ulubionych użytkownika {user_id}")
                return True
            print(f"Film {movie_id} nie był w ulubionych użytkownika {user_id}")
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania z ulubionych: {e}")
            raise

    def is_favorite(self, user_id, movie_id):
        try:
            result = (
                self.session.query(FavoriteMovie)
                .filter_by(user_id=user_id, movie_id=movie_id)
                .first()
                is not None
            )
            print(
                f"Sprawdzenie czy film {movie_id} jest w ulubionych użytkownika {user_id}: {result}"
            )
            return result
        except SQLAlchemyError as e:
            print(f"Błąd podczas sprawdzania statusu ulubionego: {e}")
            raise

    def get_user_favorites(self, user_id):
        try:
            favorites = (
                self.session.query(FavoriteMovie).filter_by(user_id=user_id).all()
            )
            print(f"Pobrano {len(favorites)} ulubionych filmów użytkownika {user_id}")
            return favorites
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania ulubionych: {e}")
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

            print(
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
            print(f"Błąd podczas pobierania ulubionych filmów: {e}")
            raise
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas pobierania ulubionych filmów: {e}")
            raise

    def get_movie_favorite_count(self, movie_id):
        try:
            count = (
                self.session.query(FavoriteMovie).filter_by(movie_id=movie_id).count()
            )
            print(f"Film {movie_id} ma {count} polubień")
            return count
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania liczby polubień: {e}")
            raise
