from app.models.recommendation import Recommendation
from app.models.movie import Movie
from app.models.user import User
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timedelta


class RecommendationRepository:
    def __init__(self, session):
        self.session = session

    def get_user_recommendations(self, user_id, limit=10, include_details=False):
        """Pobiera rekomendacje dla użytkownika"""
        query = (
            self.session.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(desc(Recommendation.score), desc(Recommendation.created_at))
            .limit(limit)
        )

        if include_details:
            query = query.options(
                joinedload(Recommendation.movie).joinedload(Movie.genres),
                joinedload(Recommendation.user),
            )

        return query.all()

    def get_by_user_and_movie(self, user_id, movie_id):
        """Pobiera konkretną rekomendację użytkownik-film"""
        return (
            self.session.query(Recommendation)
            .filter(
                Recommendation.user_id == user_id, Recommendation.movie_id == movie_id
            )
            .first()
        )

    def create_or_update(self, user_id, movie_id, score):
        """Tworzy nową lub aktualizuje istniejącą rekomendację"""
        recommendation = self.get_by_user_and_movie(user_id, movie_id)

        if recommendation:
            # Aktualizuj istniejącą
            recommendation.score = score
            recommendation.created_at = datetime.utcnow()
        else:
            # Utwórz nową
            recommendation = Recommendation(
                user_id=user_id, movie_id=movie_id, score=score
            )
            self.session.add(recommendation)

        self.session.commit()
        return recommendation

    def bulk_create_or_update(self, recommendations_data):
        """Masowo tworzy/aktualizuje rekomendacje"""
        try:
            # Usuń stare rekomendacje użytkownika
            if recommendations_data:
                user_id = recommendations_data[0]["user_id"]
                self.session.query(Recommendation).filter(
                    Recommendation.user_id == user_id
                ).delete()

            # Dodaj nowe rekomendacje
            recommendations = []
            for data in recommendations_data:
                recommendation = Recommendation(
                    user_id=data["user_id"],
                    movie_id=data["movie_id"],
                    score=data["score"],
                )
                recommendations.append(recommendation)

            self.session.add_all(recommendations)
            self.session.commit()
            return recommendations

        except Exception as e:
            self.session.rollback()
            raise e

    def delete_user_recommendations(self, user_id):
        """Usuwa wszystkie rekomendacje użytkownika"""
        try:
            deleted = (
                self.session.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .delete()
            )
            self.session.commit()
            return deleted > 0
        except Exception as e:
            self.session.rollback()
            raise e

    def get_statistics(self):
        """Pobiera statystyki rekomendacji"""
        try:
            total_recommendations = self.session.query(Recommendation).count()

            users_with_recommendations = (
                self.session.query(Recommendation.user_id).distinct().count()
            )

            avg_score = self.session.query(func.avg(Recommendation.score)).scalar()

            recent_recommendations = (
                self.session.query(Recommendation)
                .filter(
                    Recommendation.created_at >= datetime.utcnow() - timedelta(days=7)
                )
                .count()
            )

            return {
                "total_recommendations": total_recommendations,
                "users_with_recommendations": users_with_recommendations,
                "average_score": round(avg_score, 3) if avg_score else 0,
                "recent_recommendations_7_days": recent_recommendations,
            }

        except Exception as e:
            print(f"Błąd podczas pobierania statystyk rekomendacji: {e}")
            return {
                "total_recommendations": 0,
                "users_with_recommendations": 0,
                "average_score": 0,
                "recent_recommendations_7_days": 0,
            }

    def get_paginated(self, page=1, per_page=20, user_id=None):
        """Pobiera rekomendacje z paginacją"""
        query = self.session.query(Recommendation).options(
            joinedload(Recommendation.movie), joinedload(Recommendation.user)
        )

        if user_id:
            query = query.filter(Recommendation.user_id == user_id)

        query = query.order_by(desc(Recommendation.created_at))

        total = query.count()
        recommendations = query.offset((page - 1) * per_page).limit(per_page).all()

        total_pages = (total + per_page - 1) // per_page

        return {
            "recommendations": recommendations,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }
