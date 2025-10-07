from backend.app.repositories.recommendation_repository_old import RecommendationRepository
from app.services.database import db
from app.models.recommendation import Recommendation
from app.recommendation_algorithm.recommender import MovieRecommender
from functools import lru_cache
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
recommendation_repo = RecommendationRepository(db.session)


def generate_recommendations_for_user(user_id):
    """Generuje rekomendacje dla użytkownika używając algorytmu Pazzaniego-Billsusa"""
    try:
        # Inicjalizuj system rekomendacyjny
        recommender = MovieRecommender(db.session)

        # Wygeneruj rekomendacje
        result = recommender.generate_recommendations(user_id)

        if not result["success"]:
            logger.warning(
                f"Failed to generate recommendations for user {user_id}: {result['message']}"
            )
            return {
                "success": False,
                "message": result["message"],
                "recommendations": [],
            }

        logger.info(
            f"Successfully generated {len(result['recommendations'])} recommendations for user {user_id}"
        )

        return {
            "success": True,
            "message": result["message"],
            "recommendations": [
                {**rec, "created_at": datetime.utcnow().isoformat()}
                for rec in result["recommendations"]
            ],
        }

    except Exception as e:
        logger.error(f"Error in generate_recommendations_for_user: {str(e)}")
        raise Exception(
            f"Błąd podczas generowania rekomendacji dla użytkownika {user_id}: {str(e)}"
        )


def get_user_recommendations(user_id, limit=10, include_details=True):
    """Pobiera rekomendacje użytkownika z bazy danych"""
    try:
        recommendations = recommendation_repo.get_user_recommendations(
            user_id=user_id, limit=limit, include_details=include_details
        )

        if not recommendations:
            return {
                "recommendations": [],
                "message": "Brak rekomendacji. Oceń więcej filmów, aby otrzymać personalne sugestie.",
                "total": 0,
            }

        serialized_recommendations = []
        for rec in recommendations:
            rec_data = rec.serialize(include_movie=include_details)

            if include_details and rec.movie:
                # Dodaj dodatkowe informacje o filmie
                rec_data["movie"].update(
                    {
                        "genres": (
                            [genre.serialize() for genre in rec.movie.genres]
                            if rec.movie.genres
                            else []
                        ),
                        "poster_url": rec.movie.poster_url,
                        "description": rec.movie.description,
                        "release_date": (
                            rec.movie.release_date.isoformat()
                            if rec.movie.release_date
                            else None
                        ),
                    }
                )

            serialized_recommendations.append(rec_data)

        return {
            "recommendations": serialized_recommendations,
            "total": len(recommendations),
            "message": f"Znaleziono {len(recommendations)} rekomendacji",
        }

    except Exception as e:
        logger.error(f"Error in get_user_recommendations: {str(e)}")
        raise Exception(
            f"Błąd podczas pobierania rekomendacji użytkownika {user_id}: {str(e)}"
        )


def get_recommendations_paginated(page=1, per_page=20, user_id=None):
    """Pobiera rekomendacje z paginacją"""
    try:
        result = recommendation_repo.get_paginated(
            page=page, per_page=per_page, user_id=user_id
        )

        serialized_recommendations = []
        for rec in result["recommendations"]:
            rec_data = rec.serialize(include_movie=True, include_user=True)

            # Dodaj informacje o filmie
            if rec.movie:
                rec_data["movie"].update(
                    {
                        "genres": (
                            [genre.serialize() for genre in rec.movie.genres]
                            if rec.movie.genres
                            else []
                        ),
                        "poster_url": rec.movie.poster_url,
                    }
                )

            serialized_recommendations.append(rec_data)

        return {
            "recommendations": serialized_recommendations,
            "pagination": result["pagination"],
        }

    except Exception as e:
        logger.error(f"Error in get_recommendations_paginated: {str(e)}")
        raise Exception(f"Błąd podczas pobierania rekomendacji z paginacją: {str(e)}")


def refresh_user_recommendations(user_id):
    """Odświeża rekomendacje użytkownika (usuwa stare i generuje nowe)"""
    try:
        # Usuń stare rekomendacje
        deleted = recommendation_repo.delete_user_recommendations(user_id)
        logger.info(f"Deleted old recommendations for user {user_id}: {deleted}")

        # Wygeneruj nowe
        result = generate_recommendations_for_user(user_id)

        if result["success"]:
            logger.info(f"Successfully refreshed recommendations for user {user_id}")
            return {
                "success": True,
                "message": f"Pomyślnie odświeżono rekomendacje. Wygenerowano {len(result['recommendations'])} nowych sugestii.",
                "recommendations": result["recommendations"],
            }
        else:
            return result

    except Exception as e:
        logger.error(f"Error in refresh_user_recommendations: {str(e)}")
        raise Exception(
            f"Błąd podczas odświeżania rekomendacji użytkownika {user_id}: {str(e)}"
        )


def check_user_eligibility(user_id):
    """Sprawdza czy użytkownik może otrzymać rekomendacje"""
    try:
        from app.recommendation_algorithm.utils.data_preprocessor import (
            DataPreprocessor,
        )

        preprocessor = DataPreprocessor(db.session)
        is_eligible = preprocessor.check_user_eligibility(user_id)

        if is_eligible:
            return {
                "eligible": True,
                "message": "Użytkownik może otrzymać rekomendacje",
            }
        else:
            from app.recommendation_algorithm.config import MIN_USER_RATINGS

            return {
                "eligible": False,
                "message": f"Użytkownik musi oceić co najmniej {MIN_USER_RATINGS} filmów",
            }

    except Exception as e:
        logger.error(f"Error in check_user_eligibility: {str(e)}")
        raise Exception(
            f"Błąd podczas sprawdzania kwalifikowalności użytkownika {user_id}: {str(e)}"
        )


def get_recommendation_statistics():
    """Pobiera statystyki systemu rekomendacyjnego"""
    try:
        stats = recommendation_repo.get_statistics()

        # Dodaj dodatkowe statystyki
        from app.recommendation_algorithm.config import MIN_USER_RATINGS
        from app.models.user import User
        from app.models.rating import Rating

        # Liczba użytkowników kwalifikujących się do rekomendacji
        eligible_users = (
            db.session.query(User.user_id)
            .join(Rating)
            .group_by(User.user_id)
            .having(db.func.count(Rating.rating_id) >= MIN_USER_RATINGS)
            .count()
        )

        stats.update(
            {
                "min_ratings_required": MIN_USER_RATINGS,
                "eligible_users": eligible_users,
                "recommendation_coverage": (
                    round(
                        (stats["users_with_recommendations"] / eligible_users * 100), 2
                    )
                    if eligible_users > 0
                    else 0
                ),
            }
        )

        return stats

    except Exception as e:
        logger.error(f"Error in get_recommendation_statistics: {str(e)}")
        raise Exception(f"Błąd podczas pobierania statystyk rekomendacji: {str(e)}")


def get_similar_movies_for_user(user_id, movie_id, limit=5):
    """Znajduje podobne filmy dla użytkownika na podstawie jego profilu"""
    try:
        # Sprawdź czy użytkownik kwalifikuje się do rekomendacji
        eligibility = check_user_eligibility(user_id)
        if not eligibility["eligible"]:
            return {
                "success": False,
                "message": eligibility["message"],
                "similar_movies": [],
            }

        # Inicjalizuj system rekomendacyjny
        recommender = MovieRecommender(db.session)

        # Tu można by dodać metodę do znajdowania podobnych filmów
        # Na razie zwróć podobne filmy z tego samego gatunku
        from app.models.movie import Movie
        from app.models.genre import Genre

        target_movie = db.session.query(Movie).get(movie_id)
        if not target_movie:
            return {
                "success": False,
                "message": "Film nie znaleziony",
                "similar_movies": [],
            }

        # Uproszczona wersja - filmy z tego samego gatunku
        similar_movies = (
            db.session.query(Movie)
            .join(Movie.genres)
            .filter(
                Genre.genre_id.in_([g.genre_id for g in target_movie.genres]),
                Movie.movie_id != movie_id,
            )
            .limit(limit)
            .all()
        )

        return {
            "success": True,
            "message": f"Znaleziono {len(similar_movies)} podobnych filmów",
            "similar_movies": [
                movie.serialize(include_genres=True) for movie in similar_movies
            ],
        }

    except Exception as e:
        logger.error(f"Error in get_similar_movies_for_user: {str(e)}")
        raise Exception(f"Błąd podczas wyszukiwania podobnych filmów: {str(e)}")


def bulk_generate_recommendations(user_ids=None, force_refresh=False):
    """Masowo generuje rekomendacje dla wielu użytkowników"""
    try:
        if user_ids is None:
            # Pobierz wszystkich kwalifikujących się użytkowników
            from app.recommendation_algorithm.config import MIN_USER_RATINGS
            from app.models.user import User
            from app.models.rating import Rating

            user_ids_query = (
                db.session.query(User.user_id)
                .join(Rating)
                .group_by(User.user_id)
                .having(db.func.count(Rating.rating_id) >= MIN_USER_RATINGS)
            )

            if not force_refresh:
                # Pomiń użytkowników którzy już mają świeże rekomendacje (z ostatniego tygodnia)
                week_ago = datetime.utcnow() - timedelta(days=7)
                users_with_recent_recs = (
                    db.session.query(Recommendation.user_id)
                    .filter(Recommendation.created_at >= week_ago)
                    .distinct()
                    .subquery()
                )

                user_ids_query = user_ids_query.filter(
                    ~User.user_id.in_(users_with_recent_recs)
                )

            user_ids = [user_id for user_id, in user_ids_query.all()]

        results = {"successful": [], "failed": [], "total_processed": len(user_ids)}

        for user_id in user_ids:
            try:
                if force_refresh:
                    result = refresh_user_recommendations(user_id)
                else:
                    result = generate_recommendations_for_user(user_id)

                if result["success"]:
                    results["successful"].append(
                        {
                            "user_id": user_id,
                            "recommendations_count": len(result["recommendations"]),
                        }
                    )
                else:
                    results["failed"].append(
                        {"user_id": user_id, "error": result["message"]}
                    )

            except Exception as e:
                results["failed"].append({"user_id": user_id, "error": str(e)})

        logger.info(
            f"Bulk generation completed: {len(results['successful'])} successful, {len(results['failed'])} failed"
        )

        return results

    except Exception as e:
        logger.error(f"Error in bulk_generate_recommendations: {str(e)}")
        raise Exception(f"Błąd podczas masowego generowania rekomendacji: {str(e)}")


@lru_cache(maxsize=100, ttl=3600)  # Cache na godzinę
def get_recommendation_insights(user_id):
    """Pobiera wgląd w proces rekomendacji dla użytkownika"""
    try:
        from app.recommendation_algorithm.utils.data_preprocessor import (
            DataPreprocessor,
        )

        preprocessor = DataPreprocessor(db.session)

        if not preprocessor.check_user_eligibility(user_id):
            return {
                "eligible": False,
                "message": "Użytkownik nie kwalifikuje się do rekomendacji",
            }

        # Pobierz dane użytkownika
        user_ratings = preprocessor.get_user_ratings(user_id)
        positive_ratings, negative_ratings = preprocessor.get_positive_negative_ratings(
            user_ratings
        )

        # Analiza preferencji
        all_genres = []
        for _, row in user_ratings.iterrows():
            if "genres" in row and row["genres"]:
                all_genres.extend(row["genres"])

        from collections import Counter

        genre_preferences = Counter(all_genres).most_common(5)

        return {
            "eligible": True,
            "total_ratings": len(user_ratings),
            "positive_ratings": len(positive_ratings),
            "negative_ratings": len(negative_ratings),
            "preferred_genres": [
                {"genre": genre, "count": count} for genre, count in genre_preferences
            ],
            "average_user_rating": (
                user_ratings["rating"].mean() if not user_ratings.empty else 0
            ),
        }

    except Exception as e:
        logger.error(f"Error in get_recommendation_insights: {str(e)}")
        raise Exception(f"Błąd podczas pobierania wglądu w rekomendacje: {str(e)}")
