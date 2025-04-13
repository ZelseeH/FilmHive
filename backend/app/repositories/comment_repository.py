from app.models.comment import Comment
from app.models.user import User
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class CommentRepository:
    def __init__(self, session):
        self.session = session

    def add_comment(self, user_id, movie_id, comment_text):
        try:
            comment = Comment(
                user_id=user_id, movie_id=movie_id, comment_text=comment_text
            )
            self.session.add(comment)
            self.session.commit()
            print(f"Dodano komentarz do filmu {movie_id} przez użytkownika {user_id}")
            return comment
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas dodawania komentarza: {e}")
            raise

    def update_comment(self, comment_id, user_id, new_text):
        try:
            comment = (
                self.session.query(Comment)
                .filter_by(comment_id=comment_id, user_id=user_id)
                .first()
            )

            if not comment:
                print(
                    f"Komentarz {comment_id} nie istnieje lub nie należy do użytkownika {user_id}"
                )
                return None

            comment.comment_text = new_text
            self.session.commit()
            print(f"Zaktualizowano komentarz {comment_id}")
            return comment
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas aktualizacji komentarza: {e}")
            raise

    def delete_comment(self, comment_id, user_id):
        try:
            comment = (
                self.session.query(Comment)
                .filter_by(comment_id=comment_id, user_id=user_id)
                .first()
            )

            if not comment:
                print(
                    f"Komentarz {comment_id} nie istnieje lub nie należy do użytkownika {user_id}"
                )
                return False

            self.session.delete(comment)
            self.session.commit()
            print(f"Usunięto komentarz {comment_id}")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania komentarza: {e}")
            raise

    def get_comment_by_id(self, comment_id):
        try:
            comment = (
                self.session.query(Comment)
                .options(joinedload(Comment.user))
                .filter_by(comment_id=comment_id)
                .first()
            )
            return comment
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarza: {e}")
            raise

    def get_movie_comments(
        self, movie_id, page=1, per_page=10, sort_by="created_at", sort_order="desc"
    ):
        try:
            query = (
                self.session.query(Comment)
                .options(joinedload(Comment.user))
                .filter_by(movie_id=movie_id)
            )

            if sort_by == "created_at":
                if sort_order == "desc":
                    query = query.order_by(Comment.created_at.desc())
                else:
                    query = query.order_by(Comment.created_at.asc())

            total = query.count()
            comments = query.limit(per_page).offset((page - 1) * per_page).all()
            total_pages = (total + per_page - 1) // per_page if total > 0 else 0

            print(
                f"Pobrano {len(comments)} z {total} komentarzy dla filmu {movie_id} (strona {page}/{total_pages})"
            )

            return {
                "comments": [
                    comment.serialize(include_user=True) for comment in comments
                ],
                "pagination": {
                    "total": total,
                    "total_pages": total_pages,
                    "page": page,
                    "per_page": per_page,
                },
            }
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarzy: {e}")
            raise
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas pobierania komentarzy: {e}")
            raise

    def get_user_comments(self, user_id, page=1, per_page=10):
        try:
            query = (
                self.session.query(Comment)
                .options(joinedload(Comment.movie))
                .filter_by(user_id=user_id)
                .order_by(Comment.created_at.desc())
            )

            total = query.count()
            comments = query.limit(per_page).offset((page - 1) * per_page).all()

            total_pages = (total + per_page - 1) // per_page if total > 0 else 0

            print(
                f"Pobrano {len(comments)} z {total} komentarzy użytkownika {user_id} (strona {page}/{total_pages})"
            )

            return {
                "comments": [
                    comment.serialize(include_movie=True) for comment in comments
                ],
                "pagination": {
                    "total": total,
                    "total_pages": total_pages,
                    "page": page,
                    "per_page": per_page,
                },
            }
        except SQLAlchemyError as e:
            print(f"Błąd podczas pobierania komentarzy użytkownika: {e}")
            raise

    def count_movie_comments(self, movie_id):
        try:
            count = self.session.query(Comment).filter_by(movie_id=movie_id).count()
            print(f"Film {movie_id} ma {count} komentarzy")
            return count
        except SQLAlchemyError as e:
            print(f"Błąd podczas liczenia komentarzy: {e}")
            raise
