from flask import Blueprint, jsonify, request, current_app, make_response
from app.services.MovieRelationsService import MovieRelationsService
from app.services.auth_service import admin_required, staff_required

movie_relations_bp = Blueprint("movie_relations", __name__)
movie_relations_service = MovieRelationsService()


def cors_headers(f):
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            response = make_response()
        else:
            response = make_response(f(*args, **kwargs))

        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    decorated_function.__name__ = f.__name__
    return decorated_function


@movie_relations_bp.route("/movies/<int:movie_id>/actors", methods=["POST", "OPTIONS"])
@cors_headers
@staff_required
def add_actor_to_movie(movie_id):
    if request.method == "OPTIONS":
        return

    try:
        data = request.get_json()
        actor_id = data.get("actor_id")
        role = data.get("role", "")

        if not actor_id:
            return jsonify({"error": "actor_id jest wymagane"}), 400

        movie_actor = movie_relations_service.add_actor_to_movie(
            movie_id, actor_id, role
        )
        return (
            jsonify(
                {
                    "message": "Aktor został pomyślnie dodany do filmu",
                    "data": movie_actor.serialize(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding actor to movie: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas dodawania aktora do filmu"}),
            500,
        )


@movie_relations_bp.route(
    "/movies/<int:movie_id>/actors/<int:actor_id>", methods=["DELETE", "OPTIONS"]
)
@cors_headers
@staff_required
def remove_actor_from_movie(movie_id, actor_id):
    if request.method == "OPTIONS":
        return

    try:
        result = movie_relations_service.remove_actor_from_movie(movie_id, actor_id)
        if result:
            return jsonify({"message": "Aktor został pomyślnie usunięty z filmu"})
        return jsonify({"error": "Nie znaleziono aktora w tym filmie"}), 404

    except Exception as e:
        current_app.logger.error(f"Error removing actor from movie: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas usuwania aktora z filmu"}), 500


@movie_relations_bp.route(
    "/movies/<int:movie_id>/directors", methods=["POST", "OPTIONS"]
)
@cors_headers
@staff_required
def add_director_to_movie(movie_id):
    if request.method == "OPTIONS":
        return

    try:
        data = request.get_json()
        director_id = data.get("director_id")

        if not director_id:
            return jsonify({"error": "director_id jest wymagane"}), 400

        movie_director = movie_relations_service.add_director_to_movie(
            movie_id, director_id
        )
        return (
            jsonify(
                {
                    "message": "Reżyser został pomyślnie dodany do filmu",
                    "data": movie_director.serialize(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding director to movie: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas dodawania reżysera do filmu"}),
            500,
        )


@movie_relations_bp.route(
    "/movies/<int:movie_id>/directors/<int:director_id>", methods=["DELETE", "OPTIONS"]
)
@cors_headers
@staff_required
def remove_director_from_movie(movie_id, director_id):
    if request.method == "OPTIONS":
        return

    try:
        result = movie_relations_service.remove_director_from_movie(
            movie_id, director_id
        )
        if result:
            return jsonify({"message": "Reżyser został pomyślnie usunięty z filmu"})
        return jsonify({"error": "Nie znaleziono reżysera w tym filmie"}), 404

    except Exception as e:
        current_app.logger.error(f"Error removing director from movie: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas usuwania reżysera z filmu"}),
            500,
        )


@movie_relations_bp.route("/movies/<int:movie_id>/genres", methods=["POST", "OPTIONS"])
@cors_headers
@staff_required
def add_genre_to_movie(movie_id):
    if request.method == "OPTIONS":
        return

    try:
        data = request.get_json()
        genre_id = data.get("genre_id")

        if not genre_id:
            return jsonify({"error": "genre_id jest wymagane"}), 400

        movie_genre = movie_relations_service.add_genre_to_movie(movie_id, genre_id)
        return (
            jsonify(
                {
                    "message": "Gatunek został pomyślnie dodany do filmu",
                    "data": movie_genre.serialize(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding genre to movie: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas dodawania gatunku do filmu"}),
            500,
        )


@movie_relations_bp.route(
    "/movies/<int:movie_id>/genres/<int:genre_id>", methods=["DELETE", "OPTIONS"]
)
@cors_headers
@staff_required
def remove_genre_from_movie(movie_id, genre_id):
    if request.method == "OPTIONS":
        return

    try:
        result = movie_relations_service.remove_genre_from_movie(movie_id, genre_id)
        if result:
            return jsonify({"message": "Gatunek został pomyślnie usunięty z filmu"})
        return jsonify({"error": "Nie znaleziono gatunku w tym filmie"}), 404

    except Exception as e:
        current_app.logger.error(f"Error removing genre from movie: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas usuwania gatunku z filmu"}), 500


@movie_relations_bp.route("/movies/<int:movie_id>/actors", methods=["GET", "OPTIONS"])
@cors_headers
def get_movie_actors(movie_id):
    if request.method == "OPTIONS":
        return

    try:
        actors = movie_relations_service.get_movie_actors(movie_id)
        return jsonify({"actors": actors})

    except Exception as e:
        current_app.logger.error(f"Error getting movie actors: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania aktorów filmu"}), 500


@movie_relations_bp.route(
    "/movies/<int:movie_id>/directors", methods=["GET", "OPTIONS"]
)
@cors_headers
def get_movie_directors(movie_id):
    if request.method == "OPTIONS":
        return

    try:
        directors = movie_relations_service.get_movie_directors(movie_id)
        return jsonify({"directors": directors})

    except Exception as e:
        current_app.logger.error(f"Error getting movie directors: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas pobierania reżyserów filmu"}),
            500,
        )


@movie_relations_bp.route("/movies/<int:movie_id>/genres", methods=["GET", "OPTIONS"])
@cors_headers
def get_movie_genres(movie_id):
    if request.method == "OPTIONS":
        return

    try:
        genres = movie_relations_service.get_movie_genres(movie_id)
        return jsonify({"genres": genres})

    except Exception as e:
        current_app.logger.error(f"Error getting movie genres: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas pobierania gatunków filmu"}),
            500,
        )
