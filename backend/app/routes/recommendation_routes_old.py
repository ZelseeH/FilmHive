from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from app.services.auth_service import admin_required, staff_required
import time
from functools import wraps

from app.services.recommendation_service import (
    generate_recommendations_for_user,
    get_user_recommendations,
    get_recommendations_paginated,
    refresh_user_recommendations,
    check_user_eligibility,
    get_recommendation_statistics,
    get_similar_movies_for_user,
    bulk_generate_recommendations,
    get_recommendation_insights,
)

recommendations_bp = Blueprint("recommendations", __name__)


def cached_response(timeout=300):
    """Cache decorator for responses"""

    def decorator(f):
        cache = {}

        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = str(args) + str(kwargs) + str(request.args)
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data
            result = f(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result

        return decorated_function

    return decorator


def get_current_user_id():
    """Get current user ID from JWT token"""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return identity if identity else None
    except:
        return None


@recommendations_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_recommendations():
    """Generuje rekomendacje dla zalogowanego użytkownika"""
    try:
        user_id = get_jwt_identity()

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


@recommendations_bp.route("/my", methods=["GET"])
@jwt_required()
def get_my_recommendations():
    """Pobiera rekomendacje dla zalogowanego użytkownika"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 10, type=int)
        include_details = request.args.get("include_details", "true").lower() == "true"

        # Zabezpieczenie przed zbyt dużym limitem
        limit = min(limit, 50)

        result = get_user_recommendations(
            user_id=user_id, limit=limit, include_details=include_details
        )

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


@recommendations_bp.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
@staff_required
def get_user_recommendations_admin(user_id):
    """Pobiera rekomendacje konkretnego użytkownika (tylko dla staff)"""
    try:
        limit = request.args.get("limit", 10, type=int)
        include_details = request.args.get("include_details", "true").lower() == "true"

        limit = min(limit, 50)

        result = get_user_recommendations(
            user_id=user_id, limit=limit, include_details=include_details
        )

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_user_recommendations_admin: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania rekomendacji użytkownika",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/", methods=["GET"])
@jwt_required()
@staff_required
def get_all_recommendations():
    """Pobiera wszystkie rekomendacje z paginacją (tylko dla staff)"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        user_id = request.args.get("user_id", type=int)

        per_page = min(per_page, 50)

        result = get_recommendations_paginated(
            page=page, per_page=per_page, user_id=user_id
        )

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_all_recommendations: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_recommendations():
    """Odświeża rekomendacje dla zalogowanego użytkownika"""
    try:
        user_id = get_jwt_identity()

        result = refresh_user_recommendations(user_id)

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
        current_app.logger.error(f"Error in refresh_recommendations: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas odświeżania rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/eligibility", methods=["GET"])
@jwt_required()
def check_eligibility():
    """Sprawdza czy użytkownik może otrzymać rekomendacje"""
    try:
        user_id = get_jwt_identity()

        result = check_user_eligibility(user_id)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error in check_eligibility: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas sprawdzania kwalifikowalności",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/eligibility/<int:user_id>", methods=["GET"])
@jwt_required()
@staff_required
def check_user_eligibility_admin(user_id):
    """Sprawdza kwalifikowalność konkretnego użytkownika (tylko dla staff)"""
    try:
        result = check_user_eligibility(user_id)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error in check_user_eligibility_admin: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas sprawdzania kwalifikowalności użytkownika",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/similar/<int:movie_id>", methods=["GET"])
@jwt_required()
def get_similar_movies(movie_id):
    """Znajduje podobne filmy na podstawie profilu użytkownika"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 5, type=int)

        limit = min(limit, 20)

        result = get_similar_movies_for_user(user_id, movie_id, limit)

        if result["success"]:
            return (
                jsonify(
                    {
                        "similar_movies": result["similar_movies"],
                        "message": result["message"],
                        "count": len(result["similar_movies"]),
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": result["message"], "similar_movies": []}), 400

    except Exception as e:
        current_app.logger.error(f"Error in get_similar_movies: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas wyszukiwania podobnych filmów",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/insights", methods=["GET"])
@jwt_required()
def get_user_insights():
    """Pobiera wgląd w proces rekomendacji dla użytkownika"""
    try:
        user_id = get_jwt_identity()

        result = get_recommendation_insights(user_id)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_user_insights: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania wglądu w rekomendacje",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/insights/<int:user_id>", methods=["GET"])
@jwt_required()
@staff_required
def get_user_insights_admin(user_id):
    """Pobiera wgląd w rekomendacje konkretnego użytkownika (tylko dla staff)"""
    try:
        result = get_recommendation_insights(user_id)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_user_insights_admin: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania wglądu w rekomendacje użytkownika",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/statistics", methods=["GET"])
@jwt_required()
@staff_required
def get_statistics():
    """Pobiera statystyki systemu rekomendacyjnego (tylko dla staff)"""
    try:
        stats = get_recommendation_statistics()

        response = jsonify(stats)
        response.headers["Cache-Control"] = "private, max-age=300"
        return response, 200

    except Exception as e:
        current_app.logger.error(f"Error in get_statistics: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania statystyk rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/bulk-generate", methods=["POST"])
@jwt_required()
@admin_required
def bulk_generate():
    """Masowo generuje rekomendacje dla użytkowników (tylko dla admin)"""
    try:
        data = request.get_json() or {}
        user_ids = data.get("user_ids")  # Lista user_ids lub None dla wszystkich
        force_refresh = data.get("force_refresh", False)

        result = bulk_generate_recommendations(
            user_ids=user_ids, force_refresh=force_refresh
        )

        return (
            jsonify(
                {
                    "message": "Masowe generowanie rekomendacji zakończone",
                    "results": result,
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error in bulk_generate: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas masowego generowania rekomendacji",
                    "details": str(e),
                }
            ),
            500,
        )


@recommendations_bp.route("/health", methods=["GET"])
def health_check():
    """Sprawdza status systemu rekomendacyjnego"""
    try:
        from app.recommendation_algorithm.config import MIN_USER_RATINGS

        return (
            jsonify(
                {
                    "status": "healthy",
                    "algorithm": "Pazzani-Billsus Content-Based Filtering",
                    "min_ratings_required": MIN_USER_RATINGS,
                    "components": {
                        "knn_recommender": "active",
                        "naive_bayes_recommender": "active",
                        "tfidf_processor": "active",
                        "similarity_metrics": "active",
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error in health_check: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# ERROR HANDLERS
@recommendations_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Nieprawidłowe żądanie", "message": str(error)}), 400


@recommendations_bp.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({"error": "Brak autoryzacji", "message": "Wymagane zalogowanie"}),
        401,
    )


@recommendations_bp.errorhandler(403)
def forbidden(error):
    return (
        jsonify({"error": "Brak uprawnień", "message": "Niewystarczające uprawnienia"}),
        403,
    )


@recommendations_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Nie znaleziono", "message": "Zasób nie istnieje"}), 404


@recommendations_bp.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {"error": "Błąd serwera", "message": "Wystąpił wewnętrzny błąd serwera"}
        ),
        500,
    )
