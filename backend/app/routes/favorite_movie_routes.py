from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.favorite_movie_service import FavoriteMovieService

favorites_bp = Blueprint("favorites", __name__)
favorite_service = FavoriteMovieService()


@favorites_bp.route("/add", methods=["POST"])
@jwt_required()
def add_to_favorites():
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        movie_id = data.get("movie_id")

        if not movie_id:
            return jsonify({"error": "movie_id jest wymagane"}), 400

        result = favorite_service.add_to_favorites(user_id, movie_id)
        current_app.logger.info(f"User {user_id} added movie {movie_id} to favorites")
        return jsonify(result), 201
    except ValueError as e:
        current_app.logger.error(f"ValueError in add_to_favorites: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in add_to_favorites: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas dodawania do ulubionych"}), 500


@favorites_bp.route("/remove", methods=["DELETE"])
@jwt_required()
def remove_from_favorites():
    try:
        user_id = int(get_jwt_identity())
        movie_id = request.args.get("movie_id", type=int)

        if not movie_id:
            return jsonify({"error": "movie_id jest wymagane"}), 400

        result = favorite_service.remove_from_favorites(user_id, movie_id)
        if result["success"]:
            current_app.logger.info(
                f"User {user_id} removed movie {movie_id} from favorites"
            )
            return jsonify({"message": "Film usunięty z ulubionych"}), 200
        else:
            return jsonify({"error": "Film nie był w ulubionych"}), 404
    except ValueError as e:
        current_app.logger.error(f"ValueError in remove_from_favorites: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in remove_from_favorites: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas usuwania z ulubionych"}), 500


@favorites_bp.route("/check/<int:movie_id>", methods=["GET"])
@jwt_required()
def check_if_favorite(movie_id):
    try:
        user_id = int(get_jwt_identity())
        result = favorite_service.check_if_favorite(user_id, movie_id)
        current_app.logger.info(
            f"Checked if movie {movie_id} is favorite for user {user_id}: {result}"
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in check_if_favorite: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas sprawdzania statusu ulubionego"}),
            500,
        )


@favorites_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_favorites():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)

        result = favorite_service.get_user_favorite_movies(user_id, page, per_page)
        current_app.logger.info(f"Retrieved favorites for user {user_id}, page {page}")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user_favorites: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania ulubionych"}), 500


@favorites_bp.route("/count/<int:movie_id>", methods=["GET"])
def get_movie_favorite_count(movie_id):
    try:
        count = favorite_service.get_movie_favorite_count(movie_id)
        current_app.logger.info(
            f"Retrieved favorite count for movie {movie_id}: {count}"
        )
        return jsonify({"count": count}), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_movie_favorite_count: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas pobierania liczby polubień"}),
            500,
        )


@favorites_bp.route("/user/<int:user_id>/all", methods=["GET"])
def get_user_all_favorites(user_id):
    """Pobierz wszystkie ulubione filmy użytkownika (bez limitu)"""
    try:
        result = favorite_service.get_all_favorite_movies(user_id)
        current_app.logger.info(f"Retrieved all favorite movies for user {user_id}")
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f"ValueError in get_user_all_favorites: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in get_user_all_favorites: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania wszystkich ulubionych filmów"
                }
            ),
            500,
        )
