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

    def get_comment_by_id(self, comment_id):
        try:
            comment = self.comment_repository.get_comment_by_id(comment_id)
            if not comment:
                current_app.logger.info(f"Komentarz o ID {comment_id} nie istnieje")
                return None

            current_app.logger.info(f"Pobrano komentarz o ID {comment_id}")
            return comment.serialize(include_user=True, include_movie=True)
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemyError getting comment: {str(e)}")
            raise Exception(f"Nie udało się pobrać komentarza: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected error getting comment: {str(e)}")
            raise Exception(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def get_movie_comments(
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

            # Walidacja parametrów sortowania
            if sort_by not in ["created_at"]:
                sort_by = "created_at"
            if sort_order not in ["asc", "desc"]:
                sort_order = "desc"

            result = self.comment_repository.get_movie_comments(
                movie_id, page, per_page, sort_by, sort_order
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

    def get_user_comments(self, user_id, page=1, per_page=10):
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

            result = self.comment_repository.get_user_comments(user_id, page, per_page)
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
