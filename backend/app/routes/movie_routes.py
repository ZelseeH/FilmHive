from flask import Blueprint, jsonify, request
from sqlalchemy import desc

from app.services.movie_service import (
    get_all_movies,
    get_movies_paginated,
    get_movie_by_id,
    create_movie,
    delete_movie,
    filter_movies,
    get_movie_filter_options,
    get_top_rated_movies,
)


movies_bp = Blueprint("movies", __name__)


@movies_bp.route("/", methods=["GET"])
def get_movies_list():
    try:

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        genre_id = request.args.get("genre_id", type=int)

        if per_page > 10:
            per_page = 10

        result = get_movies_paginated(page, per_page, genre_id)
        return jsonify(result), 200
    except Exception as e:
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania filmów", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/all", methods=["GET"])
def get_all_movies_list():
    try:
        movies = get_all_movies()
        return jsonify(movies), 200
    except Exception as e:
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

        movie = get_movie_by_id(id, include_actors_roles=include_roles)
        if not movie:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
        return jsonify(movie), 200
    except Exception as e:
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
        movies = get_top_rated_movies(limit)
        return jsonify(movies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@movies_bp.route("/", methods=["POST"])
def add_movie():
    data = request.get_json()

    if not data or "title" not in data or "release_date" not in data:
        return jsonify({"error": "Brak wymaganych pól: title i release_date"}), 400

    try:
        new_movie = create_movie(data)
        return jsonify(new_movie), 201
    except Exception as e:
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas dodawania filmu", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/<int:id>", methods=["DELETE"])
def remove_movie(id):
    try:
        success = delete_movie(id)
        if success:
            return jsonify({"message": "Film został usunięty"}), 200
        else:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
    except Exception as e:
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas usuwania filmu", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/filter", methods=["GET"])
def filter_movies_route():
    try:
        filters = {}
        if "title" in request.args:
            filters["title"] = request.args.get("title")
        if "countries" in request.args:
            filters["countries"] = request.args.get("countries")
        if "years" in request.args:
            filters["years"] = request.args.get("years")
        if "genres" in request.args:
            filters["genres"] = request.args.get("genres")
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

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if per_page > 20:
            per_page = 20

        result = filter_movies(
            filters,
            page=page,
            per_page=per_page,
            include_actors=include_actors,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return jsonify(result), 200
    except Exception as e:
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas filtrowania filmów", "details": str(e)}
            ),
            500,
        )


@movies_bp.route("/filter-options", methods=["GET"])
def get_filter_options_route():
    try:
        options = get_movie_filter_options()
        return jsonify(options), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas pobierania opcji filtrów",
                    "details": str(e),
                }
            ),
            500,
        )
