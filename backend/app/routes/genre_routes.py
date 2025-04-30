from flask import Blueprint, jsonify, request
from app.services.genre_service import (
    get_all_genres,
    get_genre_by_id,
    create_genre,
    delete_genre,
    update_genre,
)
from app.schemas.genre_schema import GenreSchema

genres_bp = Blueprint("genres", __name__)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@genres_bp.route("/", methods=["GET"])
def get_genres():
    try:
        genres = get_all_genres()  # lista obiektów Genre
        return genres_schema.dump(genres), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/<int:id>", methods=["GET"])
def get_genre(id):
    try:
        genre = get_genre_by_id(id)  # obiekt Genre lub None
        if not genre:
            return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404
        return genre_schema.dump(genre), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/", methods=["POST"])
def add_genre():
    data = request.get_json()
    try:
        new_genre = create_genre(data)  # obiekt Genre
        return genre_schema.dump(new_genre), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/<int:id>", methods=["DELETE"])
def remove_genre(id):
    try:
        success = delete_genre(id)
        if success:
            return jsonify({"message": "Gatunek został usunięty"}), 200
        else:
            return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/<int:id>", methods=["PUT"])
def modify_genre(id):
    data = request.get_json()
    try:
        updated_genre = update_genre(id, data)  # obiekt Genre lub None
        if not updated_genre:
            return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404
        return genre_schema.dump(updated_genre), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
