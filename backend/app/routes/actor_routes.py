from flask import Blueprint, jsonify, request
from app.services.actor_service import ActorService

actors_bp = Blueprint("actors", __name__)
actor_service = ActorService()


@actors_bp.route("/", methods=["GET"])
def get_all_actors():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.get_all_actors(page, per_page)
    return jsonify(result)


@actors_bp.route("/<int:actor_id>", methods=["GET"])
def get_actor(actor_id):
    actor = actor_service.get_actor_by_id(actor_id)
    if actor:
        return jsonify(actor.serialize())
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/search", methods=["GET"])
def search_actors():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.search_actors(query, page, per_page)
    return jsonify(result)


@actors_bp.route("/", methods=["POST"])
def add_actor():
    data = request.json
    actor = actor_service.add_actor(data)
    return jsonify(actor.serialize()), 201


@actors_bp.route("/<int:actor_id>", methods=["PUT"])
def update_actor(actor_id):
    data = request.json
    actor = actor_service.update_actor(actor_id, data)
    if actor:
        return jsonify(actor.serialize())
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/<int:actor_id>", methods=["DELETE"])
def delete_actor(actor_id):
    result = actor_service.delete_actor(actor_id)
    if result:
        return jsonify({"message": "Actor deleted successfully"})
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/<int:actor_id>/movies", methods=["GET"])
def get_actor_movies(actor_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.get_actor_movies(actor_id, page, per_page)
    if result:
        return jsonify(result)
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/filter", methods=["GET"])
def filter_actors():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Zbieramy wszystkie filtry z parametrów zapytania
    filters = {}
    if "name" in request.args:
        filters["name"] = request.args.get("name")
    if "countries" in request.args:
        filters["countries"] = request.args.get("countries")
    if "years" in request.args:
        filters["years"] = request.args.get("years")
    if "gender" in request.args:
        filters["gender"] = request.args.get("gender")

    result = actor_service.filter_actors(filters, page, per_page)
    return jsonify(result)


@actors_bp.route("/birthplaces", methods=["GET"])
def get_birthplaces():
    """Pobiera unikalne miejsca urodzenia aktorów."""
    birthplaces = actor_service.get_unique_birthplaces()
    return jsonify({"birthplaces": birthplaces})
