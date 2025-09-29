from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.recommendation_service import (
    get_recommendation_status,
    generate_recommendations_for_user,
    get_user_recommendations,
    delete_user_recommendations,
    get_basic_statistics,
)

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/status", methods=["GET"])
@jwt_required()
def get_status():
    """Sprawdza status rekomendacji - główny endpoint dla UI"""
    try:
        user_id = get_jwt_identity()

        status = get_recommendation_status(user_id)

        return jsonify(status), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_status: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas sprawdzania statusu",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_recommendations():
    """Pobiera istniejące rekomendacje użytkownika"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 10, type=int)

        # Zabezpieczenie
        limit = min(limit, 50)

        result = get_user_recommendations(user_id, limit)

        response = jsonify(result)
        response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200

    except Exception as e:
        current_app.logger.error(f"Error in get_my_recommendations: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/", methods=["POST"])
@jwt_required()
def generate_recommendations():
    """Generuje nowe rekomendacje (zastępuje stare) - długa operacja!"""
    try:
        user_id = get_jwt_identity()

        # To może potrwać 5-30 sekund!
        result = generate_recommendations_for_user(user_id)

        if result["success"]:
            return (
                jsonify(
                    {
                        "message": result["message"],
                        "recommendations": result["recommendations"],
                        "count": len(result["recommendations"]),
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": result["message"], "recommendations": []}), 400

    except Exception as e:
        current_app.logger.error(f"Error in generate_recommendations: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas generowania rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/", methods=["DELETE"])
@jwt_required()
def clear_recommendations():
    """Usuwa wszystkie rekomendacje użytkownika (opcjonalne)"""
    try:
        user_id = get_jwt_identity()

        result = delete_user_recommendations(user_id)

        if result["success"]:
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["message"]}), 404

    except Exception as e:
        current_app.logger.error(f"Error in clear_recommendations: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas usuwania rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


# Opcjonalnie - dla health check
@recommendations_bp.route("/health", methods=["GET"])
def health_check():
    """Sprawdza czy system rekomendacji działa"""
    try:
        from app.recommendation_algorithm.config import MIN_USER_RATINGS

        return (
            jsonify(
                {
                    "status": "healthy",
                    "algorithm": "Pazzani-Billsus Content-Based Filtering",
                    "min_ratings_required": MIN_USER_RATINGS,
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error in health_check: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# Opcjonalnie - podstawowe statystyki dla przyszłego admin panelu
@recommendations_bp.route("/statistics", methods=["GET"])
@jwt_required()
def get_statistics():
    """Podstawowe statystyki (dla przyszłego admin panelu)"""
    try:
        # Tu można dodać sprawdzenie uprawnień w przyszłości
        stats = get_basic_statistics()

        return jsonify(stats), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_statistics: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania statystyk",
                    "details": str(e),
                }
            ),
            500,
        )


# Error handlers
@recommendations_bp.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({"error": "Brak autoryzacji", "message": "Wymagane zalogowanie"}),
        401,
    )


@recommendations_bp.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {"error": "Błąd serwera", "message": "Wystąpił wewnętrzny błąd serwera"}
        ),
        500,
    )
