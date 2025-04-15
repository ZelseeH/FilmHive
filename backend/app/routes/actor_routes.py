from flask import Blueprint, jsonify, request, current_app, make_response
from app.services.actor_service import ActorService

actors_bp = Blueprint("actors", __name__)
actor_service = ActorService()


# Dodajemy dekorator do obsługi CORS
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


@actors_bp.route("/", methods=["GET", "OPTIONS"])
@cors_headers
def get_all_actors():
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.get_all_actors(page, per_page)
    return jsonify(result)


@actors_bp.route("/<int:actor_id>", methods=["GET", "OPTIONS"])
@cors_headers
def get_actor(actor_id):
    if request.method == "OPTIONS":
        return

    actor = actor_service.get_actor_by_id(actor_id)
    if actor:
        return jsonify(actor.serialize())
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/search", methods=["GET", "OPTIONS"])
@cors_headers
def search_actors():
    if request.method == "OPTIONS":
        return

    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.search_actors(query, page, per_page)
    return jsonify(result)


@actors_bp.route("/", methods=["POST", "OPTIONS"])
@cors_headers
def add_actor():
    if request.method == "OPTIONS":
        return

    data = request.json
    actor = actor_service.add_actor(data)
    return jsonify(actor.serialize()), 201


@actors_bp.route("/<int:actor_id>", methods=["PUT", "OPTIONS"])
@cors_headers
def update_actor(actor_id):
    if request.method == "OPTIONS":
        return

    data = request.json
    actor = actor_service.update_actor(actor_id, data)
    if actor:
        return jsonify(actor.serialize())
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/<int:actor_id>", methods=["DELETE", "OPTIONS"])
@cors_headers
def delete_actor(actor_id):
    if request.method == "OPTIONS":
        return

    result = actor_service.delete_actor(actor_id)
    if result:
        return jsonify({"message": "Actor deleted successfully"})
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/<int:actor_id>/movies", methods=["GET", "OPTIONS"])
@cors_headers
def get_actor_movies(actor_id):
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.get_actor_movies(actor_id, page, per_page)
    if result:
        return jsonify(result)
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/filter", methods=["GET", "OPTIONS"])
@cors_headers
def filter_actors():
    if request.method == "OPTIONS":
        return

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        per_page = min(per_page, 100)

        filters = {}
        if "name" in request.args:
            filters["name"] = request.args.get("name")
        if "countries" in request.args:
            filters["countries"] = request.args.get("countries")
        if "years" in request.args:
            filters["years"] = request.args.get("years")
        if "gender" in request.args:
            filters["gender"] = request.args.get("gender")

        sort_by = request.args.get("sort_by", "name")
        sort_order = request.args.get("sort_order", "asc")

        valid_sort_fields = ["name", "birth_date"]
        valid_sort_orders = ["asc", "desc"]

        if sort_by not in valid_sort_fields:
            sort_by = "name"
        if sort_order.lower() not in valid_sort_orders:
            sort_order = "asc"

        result = actor_service.filter_actors(
            filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in filter_actors route: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas filtrowania aktorów",
                    "details": str(e),
                }
            ),
            500,
        )


@actors_bp.route("/birthplaces", methods=["GET", "OPTIONS"])
@cors_headers
def get_birthplaces():
    if request.method == "OPTIONS":
        return

    birthplaces = actor_service.get_unique_birthplaces()
    return jsonify({"birthplaces": birthplaces})
