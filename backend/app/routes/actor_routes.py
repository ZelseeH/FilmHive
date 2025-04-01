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
