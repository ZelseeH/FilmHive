from app.models.recommendation import Recommendation
from app.models.movie import Movie
from app.models.user import User
from app.models.rating import Rating
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from datetime import datetime
from app.recommendation_algorithm.config import MIN_USER_RATINGS


class RecommendationRepository:
    def __init__(self, session):
        self.session = session

    def get_recommendation_status(self, user_id):
        """Sprawdza status rekomendacji użytkownika - główna metoda dla UI"""
        try:
            # Sprawdź ile ocen ma użytkownik
            ratings_count = (
                self.session.query(Rating).filter(Rating.user_id == user_id).count()
            )

            # Sprawdź czy ma rekomendacje
            recommendations_count = (
                self.session.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .count()
            )

            # Pobierz datę ostatnich rekomendacji
            last_recommendation = (
                self.session.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .order_by(desc(Recommendation.created_at))
                .first()
            )

            last_generated = None
            if last_recommendation:
                last_generated = last_recommendation.created_at

            eligible = ratings_count >= MIN_USER_RATINGS
            has_recommendations = recommendations_count > 0

            return {
                "eligible": eligible,
                "has_recommendations": has_recommendations,
                "ratings_count": ratings_count,
                "min_required": MIN_USER_RATINGS,
                "recommendations_count": recommendations_count,
                "last_generated": last_generated,
                "message": self._get_status_message(
                    eligible, ratings_count, has_recommendations
                ),
            }

        except Exception as e:
            print(f"Błąd podczas sprawdzania statusu rekomendacji: {e}")
            return {
                "eligible": False,
                "has_recommendations": False,
                "ratings_count": 0,
                "min_required": MIN_USER_RATINGS,
                "recommendations_count": 0,
                "last_generated": None,
                "message": "Wystąpił błąd podczas sprawdzania statusu",
            }

    def get_user_recommendations(self, user_id, limit=10):
        """Pobiera rekomendacje użytkownika z detalami filmów"""
        query = (
            self.session.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .options(
                joinedload(Recommendation.movie).joinedload(Movie.genres),
                joinedload(Recommendation.movie).joinedload(Movie.actors),
                joinedload(Recommendation.movie).joinedload(Movie.directors),
            )
            .order_by(desc(Recommendation.score), desc(Recommendation.created_at))
            .limit(limit)
        )

        return query.all()

    def replace_user_recommendations(self, user_id, recommendations_data):
        """Zastępuje wszystkie rekomendacje użytkownika nowymi (dla POST)"""
        try:
            # Usuń stare rekomendacje
            self.session.query(Recommendation).filter(
                Recommendation.user_id == user_id
            ).delete()

            # Dodaj nowe
            new_recommendations = []
            for data in recommendations_data:
                recommendation = Recommendation(
                    user_id=user_id, movie_id=data["movie_id"], score=data["score"]
                )
                new_recommendations.append(recommendation)

            self.session.add_all(new_recommendations)
            self.session.commit()

            return new_recommendations

        except Exception as e:
            self.session.rollback()
            raise e

    def delete_user_recommendations(self, user_id):
        """Usuwa wszystkie rekomendacje użytkownika"""
        try:
            deleted_count = (
                self.session.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )

            self.session.commit()
            return deleted_count > 0

        except Exception as e:
            self.session.rollback()
            raise e

    def _get_status_message(self, eligible, ratings_count, has_recommendations):
        """Generuje odpowiedni komunikat dla UI"""
        if not eligible:
            missing = MIN_USER_RATINGS - ratings_count
            return f"Oceń jeszcze {missing} {'film' if missing == 1 else 'filmy' if missing < 5 else 'filmów'} aby otrzymać rekomendacje"

        if not has_recommendations:
            return "Możesz wygenerować swoje pierwsze rekomendacje!"

        return f"Masz {ratings_count} ocenionych filmów. Rekomendacje są gotowe!"

    # Opcjonalne - dla przyszłych statystyk/admin panelu
    def get_basic_statistics(self):
        """Podstawowe statystyki dla admin panelu (opcjonalne)"""
        try:
            total_recommendations = self.session.query(Recommendation).count()
            users_with_recommendations = (
                self.session.query(Recommendation.user_id).distinct().count()
            )

            return {
                "total_recommendations": total_recommendations,
                "users_with_recommendations": users_with_recommendations,
            }
        except Exception as e:
            print(f"Błąd podczas pobierania statystyk: {e}")
            return {"total_recommendations": 0, "users_with_recommendations": 0}
