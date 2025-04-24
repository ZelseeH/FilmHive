from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import (
    get_user_by_id,
    get_user_by_username,
    update_user_profile,
    change_user_password,
    upload_profile_picture,
    upload_background_image,
    get_recent_rated_movies,
    get_recent_favorite_movies,
    get_user_by_username,
    get_recent_watchlist_movies,
)
from werkzeug.exceptions import BadRequest
import os

user_bp = Blueprint("user", __name__)


@user_bp.before_app_request
def setup_upload_directory():
    os.makedirs(
        os.path.join(current_app.root_path, "static/uploads/users"), exist_ok=True
    )


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
        user = get_user_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile/<username>", methods=["GET"])
def get_user_profile(username):
    try:
        user = get_user_by_username(username)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        public_data = {
            "username": user.get("username"),
            "name": user.get("name"),
            "bio": user.get("bio"),
            "profile_picture": user.get("profile_picture"),
            "background_image": user.get("background_image"),
            "background_position": user.get("background_position"),
            "registration_date": user.get("registration_date"),
        }

        return jsonify(public_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data:
            raise BadRequest("Brak danych do aktualizacji")

        updated_user = update_user_profile(user_id, data)

        if not updated_user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        return jsonify(updated_user), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Wystąpił nieoczekiwany błąd"}), 500


@user_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or "current_password" not in data or "new_password" not in data:
            raise BadRequest("Brakujące dane: obecne hasło i nowe hasło są wymagane")

        result = change_user_password(
            user_id, data["current_password"], data["new_password"]
        )

        if not result:
            return jsonify({"error": "Nieprawidłowe obecne hasło"}), 401

        return jsonify({"message": "Hasło zostało zmienione pomyślnie"}), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Wystąpił nieoczekiwany błąd"}), 500


@user_bp.route("/profile-picture", methods=["POST"])
@jwt_required()
def upload_user_profile_picture():
    try:
        user_id = int(get_jwt_identity())

        if "file" not in request.files:
            return jsonify({"error": "Nie przesłano pliku"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Nie wybrano pliku"}), 400

        updated_user = upload_profile_picture(user_id, file)

        if not updated_user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        return (
            jsonify(
                {
                    "message": "Zdjęcie profilowe zaktualizowane",
                    "profile_picture": updated_user.get("profile_picture"),
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/background-image", methods=["POST"])
@jwt_required()
def upload_user_background_image():
    try:
        user_id = int(get_jwt_identity())

        if "file" not in request.files:
            return jsonify({"error": "Nie przesłano pliku"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Nie wybrano pliku"}), 400

        position_x = request.form.get("position_x", "50")
        position_y = request.form.get("position_y", "50")

        updated_user = upload_background_image(
            user_id, file, {"x": float(position_x), "y": float(position_y)}
        )

        print(f"Zaktualizowany użytkownik: {updated_user}")

        return (
            jsonify(
                {
                    "message": "Tło profilu zaktualizowane",
                    "background_image": updated_user.get("background_image"),
                    "background_position": updated_user.get("background_position"),
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Błąd w endpoincie: {str(e)}")
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile/<username>/recent-ratings", methods=["GET"])
def get_recent_rated_movies(username):
    try:
        from app.services.user_service import (
            get_user_by_username,
            get_recent_rated_movies,
        )

        user = get_user_by_username(username)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        movies = get_recent_rated_movies(user.get("id"), limit=6)
        return jsonify(movies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile/<username>/recent-favorites", methods=["GET"])
def get_recent_favorite_movies_route(username):
    try:
        user = get_user_by_username(username)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        movies = get_recent_favorite_movies(user.get("id"), limit=6)
        return jsonify(movies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile/<username>/recent-watchlist", methods=["GET"])
def get_recent_watchlist_movies_route(username):
    try:
        user = get_user_by_username(username)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        current_app.logger.info(
            f"Getting recent watchlist movies for user {user.get('id')}"
        )
        movies = get_recent_watchlist_movies(user.get("id"), limit=6)
        current_app.logger.info(f"Got {len(movies) if movies else 0} watchlist movies")

        return jsonify(movies), 200
    except Exception as e:
        current_app.logger.error(
            f"Error in get_recent_watchlist_movies_route: {str(e)}"
        )
        return jsonify({"error": str(e)}), 500
