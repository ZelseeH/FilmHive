from app.repositories.comment_repository import CommentRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app.models.movie import Movie
from app.models.user import User
from app.models.comment import Comment


class CommentService:
    def __init__(self):
        self.comment_repository = CommentRepository(db.session)

    def add_comment(self, user_id, movie_id, comment_text):
        try:
            user = db.session.get(User, user_id)
            movie = db.session.get(Movie, movie_id)

            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            if not comment_text or len(comment_text.strip()) == 0:
                raise ValueError("Treść komentarza nie może być pusta")

            if len(comment_text) > 1000:
                raise ValueError("Komentarz nie może przekraczać 1000 znaków")

            comment = self.comment_repository.add_comment(
                user_id, movie_id, comment_text
            )
            current_app.logger.info(
                f"Dodano komentarz do filmu {movie_id} przez użytkownika {user_id}"
            )
            return comment.serialize(include_user=True)
        except ValueError as e:
            current_app.logger.error(f"ValueError adding comment: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError adding comment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się dodać komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error adding comment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def update_comment(self, comment_id, user_id, new_text):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            if not new_text or len(new_text.strip()) == 0:
                raise ValueError("Treść komentarza nie może być pusta")

            if len(new_text) > 1000:
                raise ValueError("Komentarz nie może przekraczać 1000 znaków")

            comment = self.comment_repository.update_comment(
                comment_id, user_id, new_text
            )
            if not comment:
                current_app.logger.info(
                    f"Komentarz {comment_id} nie istnieje lub nie należy do użytkownika {user_id}"
                )
                return None

            current_app.logger.info(
                f"Zaktualizowano komentarz {comment_id} przez użytkownika {user_id}"
            )
            return comment.serialize(include_user=True)
        except ValueError as e:
            current_app.logger.error(f"ValueError updating comment: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError updating comment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się zaktualizować komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error updating comment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def delete_comment(self, comment_id, user_id):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

            success = self.comment_repository.delete_comment(comment_id, user_id)
            if success:
                current_app.logger.info(
                    f"Usunięto komentarz {comment_id} przez użytkownika {user_id}"
                )
            else:
                current_app.logger.info(
                    f"Komentarz {comment_id} nie istnieje lub nie należy do użytkownika {user_id}"
                )

            return success
        except ValueError as e:
            current_app.logger.error(f"ValueError deleting comment: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError deleting comment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się usunąć komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error deleting comment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_comment_by_id(self, comment_id, include_rating=False):
        try:
            comment = self.comment_repository.get_comment_by_id(comment_id)
            if not comment:
                current_app.logger.info(f"Komentarz o ID {comment_id} nie istnieje")
                return None

            current_app.logger.info(f"Pobrano komentarz o ID {comment_id}")
            return comment.serialize(
                include_user=True, include_movie=True, include_rating=include_rating
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError getting comment: {str(e)}")
            raise Exception(f"Nie udało się pobrać komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error getting comment: {str(e)}")
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_movie_comments(
        self,
        movie_id,
        page=1,
        per_page=10,
        sort_by="created_at",
        sort_order="desc",
        include_ratings=True,
    ):
        try:
            movie = db.session.get(Movie, movie_id)
            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 50:
                per_page = 50

            valid_sort_fields = ["created_at", "rating"]
            if sort_by not in valid_sort_fields:
                sort_by = "created_at"
            if sort_order not in ["asc", "desc"]:
                sort_order = "desc"

            result = self.comment_repository.get_movie_comments(
                movie_id, page, per_page, sort_by, sort_order, include_ratings
            )
            current_app.logger.info(
                f"Pobrano komentarze dla filmu {movie_id}, strona {page}, {len(result['comments'])} komentarzy"
            )
            return result
        except ValueError as e:
            current_app.logger.error(f"ValueError getting movie comments: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting movie comments: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać komentarzy: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting movie comments: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_user_comments(self, user_id, page=1, per_page=10, include_ratings=True):
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

            result = self.comment_repository.get_user_comments(
                user_id, page, per_page, include_ratings
            )
            current_app.logger.info(
                f"Pobrano komentarze użytkownika {user_id}, strona {page}, {len(result['comments'])} komentarzy"
            )
            return result
        except ValueError as e:
            current_app.logger.error(f"ValueError getting user comments: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError getting user comments: {str(e)}")
            raise Exception(f"Nie udało się pobrać komentarzy użytkownika: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting user comments: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def count_movie_comments(self, movie_id):
        try:
            movie = db.session.get(Movie, movie_id)
            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            count = self.comment_repository.count_movie_comments(movie_id)
            current_app.logger.info(f"Film {movie_id} ma {count} komentarzy")
            return count
        except ValueError as e:
            current_app.logger.error(f"ValueError counting movie comments: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError counting movie comments: {str(e)}"
            )
            raise Exception(f"Nie udało się policzyć komentarzy: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error counting movie comments: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_user_comment_for_movie(self, user_id, movie_id, include_rating=True):
        try:
            user = db.session.get(User, user_id)
            movie = db.session.get(Movie, movie_id)

            if not user:
                raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")
            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            if include_rating:
                comment, comment_data = (
                    self.comment_repository.get_user_comment_for_movie(
                        user_id, movie_id, include_rating
                    )
                )
                if not comment:
                    current_app.logger.info(
                        f"Użytkownik {user_id} nie ma komentarza dla filmu {movie_id}"
                    )
                    return None

                current_app.logger.info(
                    f"Pobrano komentarz użytkownika {user_id} dla filmu {movie_id}"
                )
                return comment_data
            else:
                comment = self.comment_repository.get_user_comment_for_movie(
                    user_id, movie_id, include_rating=False
                )
                if not comment:
                    current_app.logger.info(
                        f"Użytkownik {user_id} nie ma komentarza dla filmu {movie_id}"
                    )
                    return None

                current_app.logger.info(
                    f"Pobrano komentarz użytkownika {user_id} dla filmu {movie_id}"
                )
                return comment.serialize(include_user=True)
        except ValueError as e:
            current_app.logger.error(f"ValueError getting user comment: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError getting user comment: {str(e)}")
            raise Exception(f"Nie udało się pobrać komentarza użytkownika: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error getting user comment: {str(e)}")
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_movie_comments_with_ratings(
        self, movie_id, page=1, per_page=10, sort_by="created_at", sort_order="desc"
    ):

        try:
            movie = db.session.get(Movie, movie_id)
            if not movie:
                raise ValueError(f"Film o ID {movie_id} nie istnieje")

            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 10
            if per_page > 50:
                per_page = 50

            valid_sort_fields = ["created_at", "rating"]
            if sort_by not in valid_sort_fields:
                sort_by = "created_at"
            if sort_order not in ["asc", "desc"]:
                sort_order = "desc"

            result = self.comment_repository.get_movie_comments(
                movie_id, page, per_page, sort_by, sort_order, include_user_ratings=True
            )

            current_app.logger.info(
                f"Pobrano komentarze z ocenami dla filmu {movie_id}, strona {page}, {len(result['comments'])} komentarzy"
            )
            return result
        except ValueError as e:
            current_app.logger.error(
                f"ValueError getting movie comments with ratings: {str(e)}"
            )
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting movie comments with ratings: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać komentarzy z ocenami: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting movie comments with ratings: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_all_comments_for_staff(
        self,
        page=1,
        per_page=20,
        search=None,
        date_from=None,
        date_to=None,
        sort_by="created_at",
        sort_order="desc",
    ):
        """Pobiera wszystkie komentarze dla staff z filtrowaniem i sortowaniem"""
        try:
            # Walidacja parametrów
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 20
            if per_page > 100:  # Większy limit dla staff
                per_page = 100

            valid_sort_fields = ["created_at", "movie_title", "username"]
            if sort_by not in valid_sort_fields:
                sort_by = "created_at"
            if sort_order not in ["asc", "desc"]:
                sort_order = "desc"

            # Walidacja dat
            if date_from:
                try:
                    from datetime import datetime

                    datetime.strptime(date_from, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        "Nieprawidłowy format daty 'date_from'. Użyj YYYY-MM-DD"
                    )

            if date_to:
                try:
                    from datetime import datetime

                    datetime.strptime(date_to, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        "Nieprawidłowy format daty 'date_to'. Użyj YYYY-MM-DD"
                    )

            result = self.comment_repository.get_all_comments(
                page=page,
                per_page=per_page,
                search=search,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            current_app.logger.info(
                f"Staff pobrał wszystkie komentarze: strona {page}, {len(result['comments'])} z {result['pagination']['total']} komentarzy"
            )
            return result

        except ValueError as e:
            current_app.logger.error(
                f"ValueError getting all comments for staff: {str(e)}"
            )
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting all comments for staff: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać komentarzy: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting all comments for staff: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def update_comment_by_staff(self, comment_id, new_text, staff_user_id):
        """Aktualizuje komentarz przez staff (bez sprawdzania właściciela)"""
        try:
            # Sprawdź czy staff user istnieje
            staff_user = db.session.get(User, staff_user_id)
            if not staff_user:
                raise ValueError(f"Staff użytkownik o ID {staff_user_id} nie istnieje")

            # Sprawdź uprawnienia staff
            if not (
                staff_user.role == 1 or staff_user.role == 2
            ):  # admin lub moderator
                raise ValueError("Brak uprawnień staff do edycji komentarzy")

            # Walidacja treści komentarza
            if not new_text or len(new_text.strip()) == 0:
                raise ValueError("Treść komentarza nie może być pusta")

            if len(new_text) > 1000:
                raise ValueError("Komentarz nie może przekraczać 1000 znaków")

            comment = self.comment_repository.update_comment_by_staff(
                comment_id, new_text.strip(), staff_user_id
            )

            if not comment:
                current_app.logger.info(f"Komentarz {comment_id} nie istnieje")
                return None

            current_app.logger.info(
                f"Staff {staff_user_id} ({staff_user.username}) zaktualizował komentarz {comment_id}"
            )
            return comment.serialize(include_user=True, include_movie=True)

        except ValueError as e:
            current_app.logger.error(f"ValueError updating comment by staff: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError updating comment by staff: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Nie udało się zaktualizować komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error updating comment by staff: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def delete_comment_by_staff(self, comment_id, staff_user_id):
        """Usuwa komentarz przez staff (bez sprawdzania właściciela)"""
        try:
            # Sprawdź czy staff user istnieje
            staff_user = db.session.get(User, staff_user_id)
            if not staff_user:
                raise ValueError(f"Staff użytkownik o ID {staff_user_id} nie istnieje")

            # Sprawdź uprawnienia staff
            if not (
                staff_user.role == 1 or staff_user.role == 2
            ):  # admin lub moderator
                raise ValueError("Brak uprawnień staff do usuwania komentarzy")

            success = self.comment_repository.delete_comment_by_staff(
                comment_id, staff_user_id
            )

            if success:
                current_app.logger.info(
                    f"Staff {staff_user_id} ({staff_user.username}) usunął komentarz {comment_id}"
                )
            else:
                current_app.logger.info(f"Komentarz {comment_id} nie istnieje")

            return success

        except ValueError as e:
            current_app.logger.error(f"ValueError deleting comment by staff: {str(e)}")
            raise
        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError deleting comment by staff: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Nie udało się usunąć komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error deleting comment by staff: {str(e)}"
            )
            db.session.rollback()
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_comment_details_for_staff(self, comment_id):
        """Pobiera szczegółowe informacje o komentarzu dla staff"""
        try:
            comment_data = self.comment_repository.get_comment_with_details(comment_id)

            if not comment_data:
                current_app.logger.info(f"Komentarz o ID {comment_id} nie istnieje")
                return None

            current_app.logger.info(f"Staff pobrał szczegóły komentarza {comment_id}")
            return comment_data

        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting comment details for staff: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać szczegółów komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting comment details for staff: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_comments_statistics(self):
        """Pobiera statystyki komentarzy dla staff dashboard"""
        try:
            stats = self.comment_repository.get_comments_stats()
            current_app.logger.info("Staff pobrał statystyki komentarzy")
            return stats

        except SQLAlchemyError as e:
            current_app.logger.error(
                f"SQLAlchemyError getting comments statistics: {str(e)}"
            )
            raise Exception(f"Nie udało się pobrać statystyk komentarzy: {str(e)}")
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error getting comments statistics: {str(e)}"
            )
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def validate_staff_permissions(self, user_id, required_role=2):
        """Sprawdza czy użytkownik ma uprawnienia staff"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False, "Użytkownik nie istnieje"

            if not user.is_active:
                return False, "Konto użytkownika jest nieaktywne"

            # role: 1=admin, 2=moderator, 3=user
            if user.role > required_role:
                return False, "Brak uprawnień staff"

            return True, "Uprawnienia potwierdzone"

        except Exception as e:
            current_app.logger.error(f"Error validating staff permissions: {str(e)}")
            return False, "Błąd sprawdzania uprawnień"

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki komentarzy"""
        try:
            stats = self.comment_repository.get_basic_statistics()
            current_app.logger.info("Retrieved basic comments statistics")
            return stats
        except Exception as e:
            current_app.logger.error(f"Error getting basic statistics: {str(e)}")
            raise Exception(f"Nie udało się pobrać statystyk: {str(e)}")

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla komentarzy"""
        try:
            dashboard_data = self.comment_repository.get_dashboard_data()
            current_app.logger.info("Retrieved comments dashboard data")
            return dashboard_data
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard data: {str(e)}")
            raise Exception(f"Nie udało się pobrać danych dashboard: {str(e)}")
