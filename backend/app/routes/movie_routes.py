from flask import Blueprint, jsonify, request

from app.services.movie_service import (
    get_all_movies,
    get_movies_paginated,
    get_movie_by_id,
    create_movie,
    delete_movie,
    filter_movies,
    get_movie_filter_options,
)
from app.schemas.movie_schema import MovieSchema


movies_bp = Blueprint("movies", __name__)

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movies_bp.route("/", methods=["GET"])
def get_movies_list():
    try:

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        genre_id = request.args.get("genre_id", type=int)
<<<<<<< Updated upstream

        if per_page > 10:
            per_page = 10

        result = get_movies_paginated(page, per_page, genre_id)
        return jsonify(result), 200
=======
        user_id = get_current_user_id()
        per_page = min(per_page, 20)
        result = get_movies_paginated(page, per_page, genre_id, user_id=user_id)
        result["movies"] = movies_schema.dump(result["movies"])
        response = jsonify(result)
        response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        movies = get_all_movies()
        return jsonify(movies), 200
=======
        user_id = get_current_user_id()
        serialize_basic = request.args.get("basic", "false").lower() == "true"
        movies = get_all_movies(user_id=user_id)
        return jsonify(movies_schema.dump(movies)), 200
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

        movie = get_movie_by_id(id, include_actors_roles=include_roles)
        if not movie:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
        return jsonify(movie), 200
=======
        user_id = get_current_user_id()
        movie = get_movie_by_id(id, include_actors_roles=include_roles, user_id=user_id)
        if not movie:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
        response = jsonify(movie_schema.dump(movie))
        response.headers["Cache-Control"] = "private, max-age=120"
        return response, 200
>>>>>>> Stashed changes
    except Exception as e:
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania filmu", "details": str(e)}
            ),
            500,
        )


<<<<<<< Updated upstream
=======
@movies_bp.route("/top-rated", methods=["GET"])
def get_top_rated_movies_route():
    try:
        limit = request.args.get("limit", 10, type=int)
        include_user_rating = (
            request.args.get("include_user_rating", "true").lower() == "true"
        )
        user_id = get_current_user_id() if include_user_rating else None
        limit = min(limit, 50)
        movies = get_top_rated_movies(limit, user_id=user_id)

        # --- DEBUG: sprawdź genres przed serializacją ---
        for movie in movies:
            print(
                f"Movie: {getattr(movie, 'title', 'brak tytułu')} (ID: {getattr(movie, 'movie_id', 'brak id')})"
            )
            print("Genres:", movie.genres)
            for genre in getattr(movie, "genres", []):
                print(f"  Type: {type(genre)}")
                print(f"  genre_id: {getattr(genre, 'genre_id', None)}")
                print(f"  genre_name: {getattr(genre, 'genre_name', None)}")
                if not hasattr(genre, "genre_id"):
                    print(
                        f"UWAGA: Film '{getattr(movie, 'title', 'brak tytułu')}' (ID: {getattr(movie, 'movie_id', 'brak id')}) "
                        f"ma niepoprawny obiekt w genres: {genre} (typ: {type(genre)})"
                    )
        # --- KONIEC DEBUGA ---

        response = jsonify(movies_schema.dump(movies))
        response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in get_top_rated_movies_route: {str(e)}")
        return jsonify({"error": str(e)}), 500


>>>>>>> Stashed changes
@movies_bp.route("/", methods=["POST"])
def add_movie():
    data = request.get_json()
    if not data or "title" not in data or "release_date" not in data:
        return jsonify({"error": "Brak wymaganych pól: title i release_date"}), 400
    try:
        new_movie = create_movie(data)
        return movie_schema.dump(new_movie), 201
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
<<<<<<< Updated upstream
        filters = {}
        if "title" in request.args:
            filters["title"] = request.args.get("title")
        if "countries" in request.args:
            filters["countries"] = request.args.get("countries")
        if "years" in request.args:
            filters["years"] = request.args.get("years")
        if "genres" in request.args:
            filters["genres"] = request.args.get("genres")
=======
        filters = {
            key: request.args.get(key)
            for key in ["title", "countries", "years", "genres"]
            if key in request.args
        }
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if per_page > 20:
            per_page = 20

=======
        user_id = get_current_user_id()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 20)
>>>>>>> Stashed changes
        result = filter_movies(
            filters,
            page=page,
            per_page=per_page,
            include_actors=include_actors,
            sort_by=sort_by,
            sort_order=sort_order,
        )
<<<<<<< Updated upstream
        return jsonify(result), 200
=======
        result["movies"] = movies_schema.dump(result["movies"])
        response = jsonify(result)
        if page == 1 and not filters:
            response.headers["Cache-Control"] = "private, max-age=60"
        return response, 200
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        return jsonify(options), 200
=======
        response = jsonify(options)
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response, 200
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======


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
        result["movies"] = movies_schema.dump(result["movies"])
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
>>>>>>> Stashed changes
