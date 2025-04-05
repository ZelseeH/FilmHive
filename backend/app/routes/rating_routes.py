from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.rating_service import (
    get_rating_by_id,
    get_user_rating_for_movie,
    get_movie_ratings,
    get_user_ratings,
    get_movie_average_rating,
    create_rating,
    update_rating,
    delete_rating,
)

ratings_bp = Blueprint("ratings", __name__)


@ratings_bp.route("/movies/<int:movie_id>/ratings", methods=["GET"])
def get_ratings_for_movie(movie_id):
    """Pobiera oceny dla danego filmu."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(
            request.args.get("per_page", 10, type=int), 50
        )  # Maksymalnie 50 na stronę

        result = get_movie_ratings(movie_id, page, per_page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania ocen: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/average-rating", methods=["GET"])
def get_average_rating(movie_id):
    """Pobiera średnią ocenę dla danego filmu."""
    try:
        result = get_movie_average_rating(movie_id)
        return jsonify({"average_rating": result}), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania średniej oceny: {str(e)}"}), 500


@ratings_bp.route("/users/<int:user_id>/ratings", methods=["GET"])
def get_ratings_by_user(user_id):
    """Pobiera oceny danego użytkownika."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)

        result = get_user_ratings(user_id, page, per_page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania ocen użytkownika: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/user-rating", methods=["GET"])
@jwt_required()
def get_current_user_rating(movie_id):
    """Pobiera ocenę danego filmu dla aktualnie zalogowanego użytkownika."""
    try:
        user_id = int(get_jwt_identity())
        print(f"Current user ID: {user_id}")
        result = get_user_rating_for_movie(user_id, movie_id)
        print(f"User rating for movie {movie_id}: {result}")

        response = jsonify({"rating": result or None})
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        return response, 200
    except Exception as e:
        print(f"Error in get_current_user_rating: {str(e)}")
        return jsonify({"error": f"Błąd pobierania oceny: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/ratings", methods=["POST"])
@jwt_required()
def rate_movie(movie_id):
    """Dodaje ocenę filmu przez zalogowanego użytkownika."""
    try:
        data = request.get_json()

        if not data or "rating" not in data:
            return jsonify({"error": "Brak wymaganego pola: rating"}), 400

        rating_value = data.get("rating")

        if not isinstance(rating_value, (int, float)) or not (1 <= rating_value <= 10):
            return jsonify({"error": "Ocena musi być liczbą od 1 do 10"}), 400

        user_id = int(get_jwt_identity())
        result = create_rating(user_id, movie_id, rating_value)

        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Błąd dodawania oceny: {str(e)}"}), 500


@ratings_bp.route("/ratings/<int:rating_id>", methods=["PUT"])
@jwt_required()
def update_movie_rating(rating_id):
    """Aktualizuje ocenę filmu."""
    try:
        data = request.get_json()

        if not data or "rating" not in data:
            return jsonify({"error": "Brak wymaganego pola: rating"}), 400

        rating_value = data.get("rating")

        if not isinstance(rating_value, (int, float)) or not (1 <= rating_value <= 10):
            return jsonify({"error": "Ocena musi być liczbą od 1 do 10"}), 400

        user_id = int(get_jwt_identity())
        result = update_rating(rating_id, rating_value, user_id)

        if result is None:
            return (
                jsonify({"error": "Ocena nie istnieje lub nie masz do niej dostępu"}),
                403,
            )

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Błąd aktualizacji oceny: {str(e)}"}), 500


@ratings_bp.route("/ratings/<int:rating_id>", methods=["DELETE"])
@jwt_required()
def delete_movie_rating(rating_id):
    """Usuwa ocenę filmu."""
    try:
        user_id = int(get_jwt_identity())
        result = delete_rating(rating_id, user_id)

        if result is None:
            return (
                jsonify({"error": "Ocena nie istnieje lub nie masz do niej dostępu"}),
                403,
            )

        return jsonify({"message": "Ocena usunięta"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Błąd usuwania oceny: {str(e)}"}), 500
