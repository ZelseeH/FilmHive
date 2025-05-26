from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import desc
import time
from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from app.services.auth_service import admin_required, staff_required

from app.services.movie_service import (
    get_all_movies,
    get_movies_paginated,
    get_movie_by_id,
    create_movie,
    delete_movie,
    filter_movies,
    get_movie_filter_options,
    get_top_rated_movies,
    search_movies,
    get_all_movies_with_title_filter,
    update_movie,
    update_movie_poster,
)

movies_bp = Blueprint("movies", __name__)


def cached_response(timeout=300):
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
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return identity if identity else None
    except:
        return None


@movies_bp.route("/", methods=["GET"])
@cached_response(timeout=60)
def get_movies_list():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        genre_id = request.args.get("genre_id", type=int)
        user_id = get_current_user_id()

        per_page = min(per_page, 20)

        result = get_movies_paginated(page, per_page, genre_id, user_id=user_id)

        response = jsonify(result)
        response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in get_movies_list: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania filmów", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/all", methods=["GET"])
@cached_response(timeout=300)
def get_all_movies_list():
    try:
        user_id = get_current_user_id()
        serialize_basic = request.args.get("basic", "false").lower() == "true"

        movies = get_all_movies(serialize_basic=serialize_basic, user_id=user_id)

        response = jsonify(movies)
        response.headers["Cache-Control"] = "private, max-age=300"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in get_all_movies_list: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania filmów", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/<int:id>", methods=["GET"])
def get_movie(id):
    try:
        include_roles = request.args.get("include_roles", "false").lower() == "true"
        user_id = get_current_user_id()

        movie = get_movie_by_id(id, include_actors_roles=include_roles, user_id=user_id)
        if not movie:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404

        response = jsonify(movie)
        response.headers["Cache-Control"] = "private, max-age=120"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in get_movie: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania filmu", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/top-rated", methods=["GET"])
def get_top_rated_movies_route():
    try:
        limit = request.args.get("limit", 10, type=int)
        include_user_rating = (
            request.args.get("include_user_rating", "true").lower() == "true"
        )
        user_id = get_current_user_id() if include_user_rating else None

        limit = min(limit, 50)  # Ograniczenie maksymalnej liczby filmów

        movies = get_top_rated_movies(limit, user_id=user_id)

        response = jsonify(movies)
        response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in get_top_rated_movies_route: {str(e)}")
        return jsonify({"error": str(e)}), 500


@movies_bp.route("/", methods=["POST"])
@jwt_required()
def add_movie():
    data = request.get_json()

    if not data or "title" not in data or "release_date" not in data:
        return jsonify({"error": "Brak wymaganych pól: title i release_date"}), 400

    try:
        new_movie = create_movie(data)
        return jsonify(new_movie), 201
    except Exception as e:
        current_app.logger.error(f"Error in add_movie: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas dodawania filmu", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def remove_movie(id):
    try:
        success = delete_movie(id)
        if success:
            return jsonify({"message": "Film został usunięty"}), 200
        else:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in remove_movie: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas usuwania filmu", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/filter", methods=["GET"])
def filter_movies_route():
    try:
        filters = {
            key: request.args.get(key)
            for key in ["title", "countries", "years", "genres"]
            if key in request.args
        }

        if "rating_count_min" in request.args:
            filters["rating_count_min"] = int(request.args.get("rating_count_min"))
        if "average_rating" in request.args:
            filters["average_rating"] = float(request.args.get("average_rating"))

        sort_by = request.args.get("sort_by", "title")
        sort_order = request.args.get("sort_order", "asc")

        valid_sort_fields = ["title", "average_rating", "rating_count", "year"]
        valid_sort_orders = ["asc", "desc"]

        if sort_by not in valid_sort_fields:
            sort_by = "title"
        if sort_order.lower() not in valid_sort_orders:
            sort_order = "asc"

        include_actors = request.args.get("include_actors", "false").lower() == "true"
        user_id = get_current_user_id()

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 20)

        result = filter_movies(
            filters,
            page=page,
            per_page=per_page,
            include_actors=include_actors,
            sort_by=sort_by,
            sort_order=sort_order,
            user_id=user_id,
        )

        response = jsonify(result)
        if page == 1 and not filters:
            response.headers["Cache-Control"] = "private, max-age=60"

        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in filter_movies_route: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas filtrowania filmów", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/filter-options", methods=["GET"])
@cached_response(timeout=3600)
def get_filter_options_route():
    try:
        options = get_movie_filter_options()

        response = jsonify(options)
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in get_filter_options_route: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania opcji filtrów",
                    "details": str(e),
                }
            ),
            500,
        )


@movies_bp.route("/<int:id>/rate", methods=["POST"])
@jwt_required()
def rate_movie(id):
    try:
        user_id = get_jwt_identity()
        rating_data = request.get_json()

        if not rating_data or "rating" not in rating_data:
            return jsonify({"error": "Brak wymaganego pola: rating"}), 400

        rating = int(rating_data["rating"])
        if rating < 0 or rating > 5:
            return jsonify({"error": "Ocena musi być liczbą od 0 do 5"}), 400

        from app.services.rating_service import add_rating

        add_rating(user_id, id, rating)

        return jsonify({"message": "Film został oceniony"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in rate_movie: {str(e)}")
        return jsonify({"error": str(e)}), 500


@movies_bp.route("/<int:id>/rate", methods=["DELETE"])
@jwt_required()
def remove_rating(id):
    try:
        user_id = get_jwt_identity()
        from app.services.rating_service import delete_rating

        success = delete_rating(user_id, id)

        if success:
            return jsonify({"message": "Ocena została usunięta"}), 200
        else:
            return jsonify({"error": "Nie znaleziono oceny dla tego filmu"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in remove_rating: {str(e)}")
        return jsonify({"error": str(e)}), 500


@movies_bp.route("/search", methods=["GET"])
def search_movies_route():
    try:
        query = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        user_id = get_current_user_id()

        per_page = min(per_page, 20)

        result = search_movies(query, page=page, per_page=per_page, user_id=user_id)

        response = jsonify(
            {"results": result["movies"], "pagination": result["pagination"]}
        )
        response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in search_movies_route: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas wyszukiwania filmów",
                    "details": str(e),
                }
            ),
            500,
        )


@movies_bp.route("/getall", methods=["GET"])
def get_all_movies_with_filter():
    try:
        title_filter = request.args.get("title", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        per_page = min(per_page, 50)

        result = get_all_movies_with_title_filter(
            title_filter=title_filter if title_filter else None,
            page=page,
            per_page=per_page,
        )

        response = jsonify(result)
        response.headers["Cache-Control"] = "private, max-age=30"
        return response, 200

    except Exception as e:
        current_app.logger.error(f"Error in get_all_movies_with_filter: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania filmów", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@staff_required
def update_movie_endpoint(id):
    """
    Endpoint do edycji filmu - tylko dla staff
    """
    try:
        # Pobierz dane z formularza
        data = {}

        # Obsługa FormData i JSON
        if request.content_type and "multipart/form-data" in request.content_type:
            # FormData
            for key in request.form:
                data[key] = request.form[key]
        else:
            # JSON
            json_data = request.get_json()
            if json_data:
                data = json_data

        # Walidacja wymaganych pól
        if "title" in data and not data["title"].strip():
            return jsonify({"error": "Tytuł jest wymagany"}), 400

        # Walidacja długości tytułu
        if "title" in data and len(data["title"]) > 200:
            return jsonify({"error": "Tytuł nie może być dłuższy niż 200 znaków"}), 400

        # Walidacja czasu trwania
        if "duration_minutes" in data:
            try:
                duration = int(data["duration_minutes"])
                if duration < 1 or duration > 600:
                    return (
                        jsonify(
                            {"error": "Czas trwania musi być między 1 a 600 minut"}
                        ),
                        400,
                    )
                data["duration_minutes"] = duration
            except ValueError:
                return jsonify({"error": "Czas trwania musi być liczbą"}), 400

        # Walidacja daty premiery
        if "release_date" in data and data["release_date"]:
            try:
                from datetime import datetime

                release_date = datetime.strptime(data["release_date"], "%Y-%m-%d")
                today = datetime.now()
                if release_date > today:
                    return (
                        jsonify(
                            {
                                "error": "Data premiery nie może być późniejsza niż dzisiejsza"
                            }
                        ),
                        400,
                    )
            except ValueError:
                return jsonify({"error": "Nieprawidłowy format daty"}), 400

        # Aktualizuj film
        updated_movie = update_movie(id, data)
        if not updated_movie:
            return jsonify({"error": "Film nie został znaleziony"}), 404

        response = jsonify(
            {"message": "Film został pomyślnie zaktualizowany", "movie": updated_movie}
        )
        response.headers["Cache-Control"] = "no-cache"
        return response, 200

    except Exception as e:
        current_app.logger.error(f"Error in update_movie_endpoint: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas aktualizacji filmu", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/<int:id>/poster", methods=["POST"])
@jwt_required()
@staff_required
def upload_movie_poster_endpoint(id):
    try:
        movie_data = get_movie_by_id(id)
        if not movie_data:
            return jsonify({"error": "Film nie został znaleziony"}), 404

        if "poster" not in request.files:
            return jsonify({"error": "Brak pliku plakatu"}), 400

        file = request.files["poster"]
        if file.filename == "":
            return jsonify({"error": "Nie wybrano pliku"}), 400

        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            return (
                jsonify(
                    {
                        "error": "Nieprawidłowy format pliku. Dozwolone: PNG, JPG, JPEG, GIF, WEBP"
                    }
                ),
                400,
            )

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > 5 * 1024 * 1024:
            return jsonify({"error": "Plik jest za duży. Maksymalny rozmiar: 5MB"}), 400

        import os
        import re
        import unicodedata

        def normalize_filename(title):
            normalized = unicodedata.normalize("NFD", title)
            ascii_title = "".join(
                c for c in normalized if unicodedata.category(c) != "Mn"
            )
            ascii_title = re.sub(r"[^\w\s-]", "", ascii_title)
            ascii_title = re.sub(r"[-\s]+", "_", ascii_title)
            ascii_title = ascii_title.strip("_")
            return ascii_title

        upload_folder = os.path.join(current_app.static_folder, "posters")
        os.makedirs(upload_folder, exist_ok=True)

        movie_title = movie_data.get("title", "unknown_movie")
        normalized_title = normalize_filename(movie_title)
        filename = f"{normalized_title}.jpg"
        file_path = os.path.join(upload_folder, filename)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                current_app.logger.info(f"Removed old poster: {file_path}")
            except Exception as e:
                current_app.logger.warning(
                    f"Could not remove old poster {file_path}: {str(e)}"
                )

        file.save(file_path)

        updated_movie = update_movie_poster(id, filename)
        if not updated_movie:
            if os.path.exists(file_path):
                os.remove(file_path)
            return (
                jsonify(
                    {"error": "Nie udało się zaktualizować plakatu w bazie danych"}
                ),
                500,
            )

        poster_url = f"{request.host_url}static/posters/{filename}"

        response = jsonify(
            {
                "message": "Plakat został pomyślnie zaktualizowany",
                "movie": updated_movie,
                "poster_url": poster_url,
                "filename": filename,
            }
        )
        response.headers["Cache-Control"] = "no-cache"
        return response, 200

    except Exception as e:
        current_app.logger.error(f"Error in upload_movie_poster_endpoint: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas uploadu plakatu", "details": str(e)}
            ),
            500,
        )


# STATISTICS & DASHBOARD ENDPOINTS


@movies_bp.route("/statistics", methods=["GET"])
@staff_required
def get_movies_statistics():
    """Pobiera podstawowe statystyki filmów"""
    try:
        from app.services.movie_service import get_basic_statistics

        stats = get_basic_statistics()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting movies statistics: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania statystyk filmów"}), 500


@movies_bp.route("/dashboard", methods=["GET"])
@staff_required
def get_movies_dashboard():
    """Pobiera dane dashboard dla filmów"""
    try:
        from app.services.movie_service import get_dashboard_data

        dashboard_data = get_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting movies dashboard: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania dashboard filmów"}), 500
