from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.watchlist_service import WatchlistService

watchlist_bp = Blueprint("watchlist", __name__)
watchlist_service = WatchlistService()


@watchlist_bp.route("/add", methods=["POST"])
@jwt_required()
def add_to_watchlist():
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        movie_id = data.get("movie_id")

        if not movie_id:
            return jsonify({"error": "movie_id jest wymagane"}), 400

        result = watchlist_service.add_to_watchlist(user_id, movie_id)
        current_app.logger.info(f"User {user_id} added movie {movie_id} to watchlist")
        return jsonify(result), 201
    except ValueError as e:
        current_app.logger.error(f"ValueError in add_to_watchlist: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in add_to_watchlist: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas dodawania do listy do obejrzenia"}
            ),
            500,
        )


@watchlist_bp.route("/remove", methods=["DELETE"])
@jwt_required()
def remove_from_watchlist():
    try:
        user_id = int(get_jwt_identity())
        movie_id = request.args.get("movie_id", type=int)

        if not movie_id:
            return jsonify({"error": "movie_id jest wymagane"}), 400

        result = watchlist_service.remove_from_watchlist(user_id, movie_id)
        if result["success"]:
            current_app.logger.info(
                f"User {user_id} removed movie {movie_id} from watchlist"
            )
            return jsonify({"message": "Film usunięty z listy do obejrzenia"}), 200
        else:
            return jsonify({"error": "Film nie był na liście do obejrzenia"}), 404
    except ValueError as e:
        current_app.logger.error(f"ValueError in remove_from_watchlist: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in remove_from_watchlist: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas usuwania z listy do obejrzenia"}),
            500,
        )


@watchlist_bp.route("/check/<int:movie_id>", methods=["GET"])
@jwt_required()
def check_if_in_watchlist(movie_id):
    try:
        user_id = int(get_jwt_identity())
        result = watchlist_service.check_if_in_watchlist(user_id, movie_id)
        current_app.logger.info(
            f"Checked if movie {movie_id} is in watchlist for user {user_id}: {result}"
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in check_if_in_watchlist: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas sprawdzania statusu listy do obejrzenia"
                }
            ),
            500,
        )


@watchlist_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_watchlist():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)

        result = watchlist_service.get_user_watchlist(user_id, page, per_page)
        current_app.logger.info(f"Retrieved watchlist for user {user_id}, page {page}")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user_watchlist: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas pobierania listy do obejrzenia"}),
            500,
        )


@watchlist_bp.route("/user/recent", methods=["GET"])
@jwt_required()
def get_recent_watchlist():
    try:
        user_id = int(get_jwt_identity())
        limit = min(request.args.get("limit", 6, type=int), 20)

        result = watchlist_service.get_recent_watchlist_movies(user_id, limit)
        current_app.logger.info(f"Retrieved recent watchlist for user {user_id}")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_recent_watchlist: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania ostatnich filmów z listy do obejrzenia"
                }
            ),
            500,
        )


@watchlist_bp.route("/user/<int:user_id>/recent", methods=["GET"])
def get_user_recent_watchlist(user_id):
    try:
        limit = min(request.args.get("limit", 6, type=int), 20)

        result = watchlist_service.get_recent_watchlist_movies(user_id, limit)
        current_app.logger.info(f"Retrieved recent watchlist for user {user_id}")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user_recent_watchlist: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania ostatnich filmów z listy do obejrzenia"
                }
            ),
            500,
        )


@watchlist_bp.route("/user/recent/<int:movie_id>", methods=["DELETE"])
@jwt_required()
def remove_from_recent_watchlist(movie_id):
    try:
        user_id = int(get_jwt_identity())

        result = watchlist_service.remove_from_watchlist(user_id, movie_id)
        if result["success"]:
            current_app.logger.info(
                f"User {user_id} removed movie {movie_id} from watchlist via recent list"
            )
            return jsonify({"message": "Film usunięty z listy do obejrzenia"}), 200
        else:
            return jsonify({"error": "Film nie był na liście do obejrzenia"}), 404
    except ValueError as e:
        current_app.logger.error(
            f"ValueError in remove_from_recent_watchlist: {str(e)}"
        )
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in remove_from_recent_watchlist: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas usuwania z listy do obejrzenia"}),
            500,
        )


@watchlist_bp.route("/user/<int:user_id>/all", methods=["GET"])
def get_user_all_watchlist(user_id):
    """Pobierz wszystkie filmy z watchlisty użytkownika (bez limitu)"""
    try:
        result = watchlist_service.get_all_watchlist_movies(user_id)
        current_app.logger.info(f"Retrieved all watchlist movies for user {user_id}")
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f"ValueError in get_user_all_watchlist: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in get_user_all_watchlist: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania wszystkich filmów z listy do obejrzenia"
                }
            ),
            500,
        )
