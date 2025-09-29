from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from app.services.rating_service import (
    get_rating_by_id,
    get_user_rating_for_movie,
    get_movie_ratings,
    get_user_ratings,
    get_movie_average_rating,
    get_movie_rating_count,
    get_movie_rating_stats,
    create_rating,
    update_rating,
    delete_rating,
)

ratings_bp = Blueprint("ratings", __name__)


def validate_movie_release_date(movie_id):
    """Sprawdza czy film już wyszedł"""
    try:
        from app.services.movie_service import get_movie_by_id

        movie = get_movie_by_id(movie_id)
        if not movie:
            return False, "Film nie istnieje"

        if movie.get("release_date"):
            release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d").date()
            today = date.today()
            if release_date > today:
                return False, "Nie można ocenić filmu, który jeszcze nie miał premiery"

        return True, None
    except Exception as e:
        return False, f"Błąd sprawdzania daty premiery: {str(e)}"


@ratings_bp.route("/movies/<int:movie_id>/ratings", methods=["GET"])
def get_ratings_for_movie(movie_id):
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)

        result = get_movie_ratings(movie_id, page, per_page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania ocen: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/average-rating", methods=["GET"])
def get_average_rating(movie_id):
    try:
        result = get_movie_average_rating(movie_id)
        return jsonify({"average_rating": result}), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania średniej oceny: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/rating-count", methods=["GET"])
def get_rating_count(movie_id):
    try:
        result = get_movie_rating_count(movie_id)
        return jsonify({"rating_count": result}), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania liczby ocen: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/rating-stats", methods=["GET"])
def get_rating_stats(movie_id):
    try:
        result = get_movie_rating_stats(movie_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Błąd pobierania statystyk ocen: {str(e)}"}), 500


@ratings_bp.route("/users/<int:user_id>/ratings", methods=["GET"])
def get_ratings_by_user(user_id):
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
    try:
        user_id = int(get_jwt_identity())
        print(f"Current user ID: {user_id}")

        # Sprawdź datę premiery
        is_released, error_msg = validate_movie_release_date(movie_id)
        if not is_released:
            return (
                jsonify({"rating": None}),
                200,
            )  # Zwróć null dla nieopublikowanych filmów

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
    try:
        # WALIDACJA DATY PREMIERY
        is_released, error_msg = validate_movie_release_date(movie_id)
        if not is_released:
            return jsonify({"error": error_msg}), 400

        data = request.get_json()

        if not data or "rating" not in data:
            return jsonify({"error": "Brak wymaganego pola: rating"}), 400

        rating_value = data.get("rating")

        if not isinstance(rating_value, (int, float)) or not (1 <= rating_value <= 10):
            return jsonify({"error": "Ocena musi być liczbą od 1 do 10"}), 400

        user_id = int(get_jwt_identity())
        result = create_rating(user_id, movie_id, rating_value)

        stats = get_movie_rating_stats(movie_id)
        result.update(stats)

        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Błąd dodawania oceny: {str(e)}"}), 500


@ratings_bp.route("/ratings/<int:rating_id>", methods=["PUT"])
@jwt_required()
def update_movie_rating(rating_id):
    try:
        data = request.get_json()

        if not data or "rating" not in data:
            return jsonify({"error": "Brak wymaganego pola: rating"}), 400

        rating_value = data.get("rating")

        if not isinstance(rating_value, (int, float)) or not (1 <= rating_value <= 10):
            return jsonify({"error": "Ocena musi być liczbą od 1 do 10"}), 400

        user_id = int(get_jwt_identity())

        # Pobierz movie_id z oceny przed aktualizacją
        rating_info = get_rating_by_id(rating_id)
        if rating_info and rating_info.get("movie_id"):
            movie_id = rating_info["movie_id"]
            # WALIDACJA DATY PREMIERY
            is_released, error_msg = validate_movie_release_date(movie_id)
            if not is_released:
                return jsonify({"error": error_msg}), 400

        result = update_rating(rating_id, rating_value, user_id)

        if result is None:
            return (
                jsonify({"error": "Ocena nie istnieje lub nie masz do niej dostępu"}),
                403,
            )

        movie_id = result.get("movie_id")
        if movie_id:
            stats = get_movie_rating_stats(movie_id)
            result.update(stats)

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Błąd aktualizacji oceny: {str(e)}"}), 500


@ratings_bp.route("/movies/<int:movie_id>/user-rating", methods=["DELETE"])
@jwt_required()
def delete_movie_rating(movie_id):
    try:
        # WALIDACJA DATY PREMIERY
        is_released, error_msg = validate_movie_release_date(movie_id)
        if not is_released:
            return jsonify({"error": error_msg}), 400

        user_id = int(get_jwt_identity())
        print(f"Deleting rating for user {user_id} and movie {movie_id}")

        rating_value = get_user_rating_for_movie(user_id, movie_id)

        if not rating_value:
            return jsonify({"error": "Ocena nie istnieje"}), 404

        result = delete_rating(user_id, movie_id)

        if result is None:
            return (
                jsonify({"error": "Ocena nie istnieje lub nie masz do niej dostępu"}),
                403,
            )

        return jsonify({"message": "Ocena usunięta", **result}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error in delete_movie_rating: {str(e)}")
        return jsonify({"error": f"Błąd usuwania oceny: {str(e)}"}), 500
