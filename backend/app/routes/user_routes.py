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
    update_user_email,
)
from werkzeug.exceptions import BadRequest
import os
from app.services.auth_service import admin_required, staff_required

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

        # ✅ Używaj serialize() zamiast ręcznego tworzenia dict
        user_data = user.serialize() if hasattr(user, "serialize") else user

        public_data = {
            "username": user_data.get("username"),
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "profile_picture": user_data.get("profile_picture"),  # ✅ Już przetworzone
            "background_image": user_data.get(
                "background_image"
            ),  # ✅ Już przetworzone
            "background_position": user_data.get("background_position"),
            "registration_date": user_data.get("registration_date"),
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


@user_bp.route("/update-email", methods=["POST"])
@jwt_required()
def update_email():
    """Endpoint do aktualizacji emailu użytkownika z weryfikacją hasła"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or "email" not in data or "current_password" not in data:
            return jsonify({"error": "Brakujący email lub obecne hasło"}), 400

        new_email = data["email"]
        current_password = data["current_password"]

        # Wywołaj service z weryfikacją hasła
        result = update_user_email(user_id, new_email, current_password)

        if not result:
            return jsonify({"error": "Nie znaleziono użytkownika"}), 404

        return (
            jsonify(
                {"message": "Email został zaktualizowany pomyślnie", "user": result}
            ),
            200,
        )

    except ValueError as e:
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


@user_bp.route("/search", methods=["GET"])
def search_users_route():
    try:
        query = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        from app.services.user_service import search_users

        result = search_users(query, page, per_page)
        return jsonify(result), 200
    except Exception as e:
        return (
            jsonify(
                {"error": f"Wystąpił błąd podczas wyszukiwania użytkowników: {str(e)}"}
            ),
            500,
        )


# STATISTICS & DASHBOARD ENDPOINTS


@user_bp.route("/statistics", methods=["GET"])
@staff_required
def get_users_statistics():
    """Pobiera podstawowe statystyki użytkowników"""
    try:
        from app.services.user_service import get_basic_statistics

        stats = get_basic_statistics()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting users statistics: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania statystyk użytkowników"}), 500


@user_bp.route("/dashboard", methods=["GET"])
@staff_required
def get_users_dashboard():
    """Pobiera dane dashboard dla użytkowników"""
    try:
        from app.services.user_service import get_dashboard_data

        dashboard_data = get_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting users dashboard: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania dashboard użytkowników"}), 500


@user_bp.route("/profile/<username>/all-ratings", methods=["GET"])
def get_all_rated_movies_route(username):
    """Pobierz wszystkie ocenione filmy użytkownika (bez limitu)"""
    try:
        user = get_user_by_username(username)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        from app.services.user_service import get_all_rated_movies

        movies = get_all_rated_movies(user.get("id"))
        current_app.logger.info(
            f"Retrieved all {len(movies)} rated movies for user {username}"
        )
        return jsonify(movies), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_all_rated_movies_route: {str(e)}")
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile/<username>/all-favorites", methods=["GET"])
def get_all_favorite_movies_route(username):
    """Pobierz wszystkie ulubione filmy użytkownika (bez limitu)"""
    try:
        user = get_user_by_username(username)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        from app.services.user_service import get_all_favorite_movies

        movies = get_all_favorite_movies(user.get("id"))
        current_app.logger.info(
            f"Retrieved all {len(movies)} favorite movies for user {username}"
        )
        return jsonify(movies), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_all_favorite_movies_route: {str(e)}")
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile/<username>/all-watchlist", methods=["GET"])
def get_all_watchlist_movies_route(username):
    """Pobierz wszystkie filmy z watchlisty użytkownika (bez limitu)"""
    try:
        user = get_user_by_username(username)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        from app.services.user_service import get_all_watchlist_movies

        movies = get_all_watchlist_movies(user.get("id"))
        current_app.logger.info(f"Retrieved all watchlist movies for user {username}")
        return jsonify(movies), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_all_watchlist_movies_route: {str(e)}")
        return jsonify({"error": str(e)}), 500
