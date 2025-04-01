from app.models.rating import Rating
from app.models.movie import Movie
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError


class RatingRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, rating_id):
        """Pobiera ocenę na podstawie ID."""
        return self.session.get(Rating, rating_id)

    def get_by_user_and_movie(self, user_id, movie_id):
        """Pobiera ocenę danego użytkownika dla danego filmu."""
        return (
            self.session.query(Rating)
            .filter(Rating.user_id == user_id, Rating.movie_id == movie_id)
            .first()
        )

    def get_movie_ratings(self, movie_id, page=1, per_page=10):
        """Pobiera oceny dla danego filmu z paginacją."""
        query = self.session.query(Rating).filter(Rating.movie_id == movie_id)

        total = (
            self.session.query(func.count())
            .filter(Rating.movie_id == movie_id)
            .scalar()
        )

        ratings = (
            query.order_by(Rating.rated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "ratings": ratings,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def get_user_ratings(self, user_id, page=1, per_page=10):
        """Pobiera oceny danego użytkownika z paginacją."""
        query = self.session.query(Rating).filter(Rating.user_id == user_id)

        total = (
            self.session.query(func.count()).filter(Rating.user_id == user_id).scalar()
        )

        ratings = (
            query.order_by(Rating.rated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "ratings": ratings,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def get_movie_average_rating(self, movie_id):
        """Pobiera średnią ocenę dla danego filmu."""
        return (
            self.session.query(func.avg(Rating.rating))
            .filter(Rating.movie_id == movie_id)
            .scalar()
        ) or None

    def add(self, rating):
        """Dodaje nową ocenę."""
        try:
            self.session.add(rating)
            self.session.commit()
            return rating
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas dodawania oceny: {e}")
            return None

    def update(self, rating_id, new_rating_value):
        """Aktualizuje wartość oceny."""
        try:
            rating = self.get_by_id(rating_id)
            if rating:
                rating.rating = new_rating_value
                self.session.commit()
                return rating
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas aktualizacji oceny: {e}")
            return None

    def delete(self, rating_id):
        """Usuwa ocenę na podstawie ID."""
        try:
            rating = self.get_by_id(rating_id)
            if rating:
                self.session.delete(rating)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania oceny: {e}")
            return False

    def delete_by_user_and_movie(self, user_id, movie_id):
        """Usuwa ocenę danego użytkownika dla danego filmu."""
        try:
            rating = self.get_by_user_and_movie(user_id, movie_id)
            if rating:
                self.session.delete(rating)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Błąd podczas usuwania oceny użytkownika dla filmu: {e}")
            return False
