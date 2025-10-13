from app.repositories.recommendation_repository import RecommendationRepository
from app.services.database import db
from app.recommendation_algorithm.recommender import MovieRecommender
import logging

logger = logging.getLogger(__name__)
recommendation_repo = RecommendationRepository(db.session)


def get_recommendation_status(user_id):
    """Główna metoda - sprawdza status rekomendacji dla UI"""
    try:
        status = recommendation_repo.get_recommendation_status(user_id)
        logger.info(
            f"Status check for user {user_id}: eligible={status['eligible']}, has_recs={status['has_recommendations']}"
        )
        return status

    except Exception as e:
        logger.error(f"Error in get_recommendation_status: {str(e)}")
        raise Exception(f"Błąd podczas sprawdzania statusu rekomendacji: {str(e)}")


def generate_recommendations_for_user(user_id):
    """Generuje nowe rekomendacje (zastępuje stare)"""
    try:
        # Sprawdź czy użytkownik kwalifikuje się
        status = recommendation_repo.get_recommendation_status(user_id)
        if not status["eligible"]:
            return {
                "success": False,
                "message": status["message"],
                "recommendations": [],
            }

        # Inicjalizuj algorytm
        recommender = MovieRecommender(db.session)

        # Wygeneruj rekomendacje
        result = recommender.generate_recommendations(user_id)

        if not result["success"]:
            logger.warning(f"Algorithm failed for user {user_id}: {result['message']}")
            return result

        logger.info(
            f"Successfully generated {len(result['recommendations'])} recommendations for user {user_id}"
        )
        return result

    except Exception as e:
        # POPRAWKA: Dodaj pełny traceback dla diagnozy
        import traceback

        logger.error(f"Error in generate_recommendations_for_user: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")  # Pełny stack trace
        raise Exception(f"Błąd podczas generowania rekomendacji: {str(e)}")


def get_user_recommendations(user_id, limit=10):
    """Pobiera istniejące rekomendacje użytkownika"""
    try:
        recommendations = recommendation_repo.get_user_recommendations(user_id, limit)

        if not recommendations:
            return {
                "recommendations": [],
                "count": 0,
                "message": "Brak rekomendacji. Wygeneruj swoje pierwsze sugestie!",
            }

        # Serializuj rekomendacje z detalami filmów
        serialized_recommendations = []
        for rec in recommendations:
            rec_data = rec.serialize(include_movie=True)

            # Dodaj dodatkowe informacje o filmie
            if rec.movie:
                # Użyj metody serialize z modelu Movie z wszystkimi relacjami
                movie_data = rec.movie.serialize(
                    include_genres=True, include_actors=True, include_directors=True
                )
                rec_data["movie"] = movie_data

            serialized_recommendations.append(rec_data)

        return {
            "recommendations": serialized_recommendations,
            "count": len(recommendations),
            "message": f"Znaleziono {len(recommendations)} rekomendacji",
            "last_generated": (
                recommendations[0].created_at.isoformat() if recommendations else None
            ),
        }

    except Exception as e:
        logger.error(f"Error in get_user_recommendations: {str(e)}")
        raise Exception(f"Błąd podczas pobierania rekomendacji: {str(e)}")


def delete_user_recommendations(user_id):
    """Usuwa wszystkie rekomendacje użytkownika"""
    try:
        deleted = recommendation_repo.delete_user_recommendations(user_id)

        if deleted:
            logger.info(f"Deleted recommendations for user {user_id}")
            return {"success": True, "message": "Rekomendacje zostały usunięte"}
        else:
            return {"success": False, "message": "Brak rekomendacji do usunięcia"}

    except Exception as e:
        logger.error(f"Error in delete_user_recommendations: {str(e)}")
        raise Exception(f"Błąd podczas usuwania rekomendacji: {str(e)}")


# Opcjonalne - dla przyszłego admin panelu
def get_basic_statistics():
    """Podstawowe statystyki dla admin panelu"""
    try:
        stats = recommendation_repo.get_basic_statistics()
        logger.info(f"Retrieved recommendation statistics: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error in get_basic_statistics: {str(e)}")
        raise Exception(f"Błąd podczas pobierania statystyk: {str(e)}")
