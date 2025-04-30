from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
import os

from app.services.user_service import (
    get_user_by_id,
    get_user_by_username,
    update_user_profile,
    change_user_password,
    upload_profile_picture,
    upload_background_image,
<<<<<<< Updated upstream
=======
    get_recent_rated_movies,
    get_recent_favorite_movies,
    get_recent_watchlist_movies,
    search_users,
>>>>>>> Stashed changes
)
from app.schemas.user_schema import UserSchema
from app.schemas.movie_schema import MovieSchema

user_bp = Blueprint("user", __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@user_bp.before_app_request
def setup_upload_directory():
    os.makedirs(
        os.path.join(current_app.root_path, "static/uploads/users"), exist_ok=True
    )


def error_response(message: str, code: int = 400):
    return jsonify({"error": message}), code


def success_response(data: dict, code: int = 200):
    return jsonify(data), code


def validate_file_upload(field_name: str):
    if field_name not in request.files:
        raise BadRequest("Nie przesłano pliku")
    file = request.files[field_name]
    if file.filename == "":
        raise BadRequest("Nie wybrano pliku")
    return file


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
        user = get_user_by_id(user_id)
        if not user:
            return error_response("Użytkownik nie znaleziony", 404)
        return success_response(user_schema.dump(user))
    except Exception as e:
        return error_response(str(e), 500)


@user_bp.route("/profile/<username>", methods=["GET"])
def get_user_profile(username):
    try:
        user = get_user_by_username(username)
        if not user:
            return error_response("Użytkownik nie znaleziony", 404)
        # Jeśli chcesz tylko wybrane pola publiczne:
        public_fields = [
            "username",
            "name",
            "bio",
            "profile_picture",
            "background_image",
            "background_position",
            "registration_date",
        ]
        public_data = {
            field: user_schema.dump(user).get(field) for field in public_fields
        }
        return success_response(public_data)
    except Exception as e:
        return error_response(str(e), 500)


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
            return error_response("Użytkownik nie znaleziony", 404)
        return success_response(user_schema.dump(updated_user))
    except BadRequest as e:
        return error_response(str(e), 400)
    except Exception:
        return error_response("Wystąpił nieoczekiwany błąd", 500)


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
            return error_response("Nieprawidłowe obecne hasło", 401)
        return success_response({"message": "Hasło zostało zmienione pomyślnie"})
    except BadRequest as e:
        return error_response(str(e), 400)
    except Exception:
        return error_response("Wystąpił nieoczekiwany błąd", 500)


@user_bp.route("/profile-picture", methods=["POST"])
@jwt_required()
def upload_user_profile_picture():
    try:
        user_id = int(get_jwt_identity())
        file = validate_file_upload("file")
        updated_user = upload_profile_picture(user_id, file)
        if not updated_user:
            return error_response("Użytkownik nie znaleziony", 404)
        return success_response(
            {
                "message": "Zdjęcie profilowe zaktualizowane",
                "profile_picture": user_schema.dump(updated_user).get(
                    "profile_picture"
                ),
            }
        )
    except BadRequest as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)


@user_bp.route("/background-image", methods=["POST"])
@jwt_required()
def upload_user_background_image():
    try:
        user_id = int(get_jwt_identity())
        file = validate_file_upload("file")
        position_x = request.form.get("position_x", "50")
        position_y = request.form.get("position_y", "50")
        updated_user = upload_background_image(
            user_id,
            file,
            {"x": float(position_x), "y": float(position_y)},
        )
        return success_response(
            {
                "message": "Tło profilu zaktualizowane",
                "background_image": user_schema.dump(updated_user).get(
                    "background_image"
                ),
                "background_position": user_schema.dump(updated_user).get(
                    "background_position"
                ),
            }
        )
    except BadRequest as e:
        return error_response(str(e), 400)
    except Exception as e:
<<<<<<< Updated upstream
        print(f"Błąd w endpoincie: {str(e)}")
        return jsonify({"error": str(e)}), 500
=======
        return error_response(str(e), 500)


@user_bp.route("/profile/<username>/recent-ratings", methods=["GET"])
def get_recent_rated_movies_route(username):
    try:
        user = get_user_by_username(username)
        if not user:
            return error_response("Użytkownik nie znaleziony", 404)
        movies = get_recent_rated_movies(user.user_id, limit=6)
        return success_response(movies_schema.dump(movies))
    except Exception as e:
        return error_response(str(e), 500)


@user_bp.route("/profile/<username>/recent-favorites", methods=["GET"])
def get_recent_favorite_movies_route(username):
    try:
        user = get_user_by_username(username)
        if not user:
            return error_response("Użytkownik nie znaleziony", 404)
        movies = get_recent_favorite_movies(user.user_id, limit=6)
        return success_response(movies_schema.dump(movies))
    except Exception as e:
        return error_response(str(e), 500)


@user_bp.route("/profile/<username>/recent-watchlist", methods=["GET"])
def get_recent_watchlist_movies_route(username):
    try:
        user = get_user_by_username(username)
        if not user:
            return error_response("Użytkownik nie znaleziony", 404)
        current_app.logger.info(
            f"Getting recent watchlist movies for user {user.user_id}"
        )
        movies = get_recent_watchlist_movies(user.user_id, limit=6)
        current_app.logger.info(f"Got {len(movies) if movies else 0} watchlist movies")
        return success_response(movies_schema.dump(movies))
    except Exception as e:
        current_app.logger.error(
            f"Error in get_recent_watchlist_movies_route: {str(e)}"
        )
        return error_response(str(e), 500)


@user_bp.route("/search", methods=["GET"])
def search_users_route():
    try:
        query = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        result = search_users(query, page, per_page)
        result["users"] = users_schema.dump(result["users"])
        return success_response(result)
    except Exception as e:
        return error_response(
            f"Wystąpił błąd podczas wyszukiwania użytkowników: {str(e)}", 500
        )
>>>>>>> Stashed changes
