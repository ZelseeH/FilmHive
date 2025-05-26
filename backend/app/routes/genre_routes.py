from flask import Blueprint, jsonify, request
from app.services.genre_service import (
    get_all_genres,
    get_genre_by_id,
    create_genre,
    delete_genre,
    update_genre,
    get_basic_statistics,
    get_dashboard_data,
)
from app.services.auth_service import staff_required

genres_bp = Blueprint("genres", __name__)


@genres_bp.route("/", methods=["GET"])
def get_genres():
    try:
        genres = get_all_genres()
        return jsonify(genres), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/<int:id>", methods=["GET"])
def get_genre(id):
    try:
        genre = get_genre_by_id(id)
        if not genre:
            return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404
        return jsonify(genre), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/", methods=["POST"])
def add_genre():
    data = request.get_json()

    try:
        new_genre = create_genre(data)
        return jsonify(new_genre), 201
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
        updated_genre = update_genre(id, data)

        if not updated_genre:
            return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404

        return jsonify(updated_genre), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@genres_bp.route("/statistics", methods=["GET"])
@staff_required
def get_genres_statistics():
    """Pobiera podstawowe statystyki gatunków"""
    try:
        stats = get_basic_statistics()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": "Błąd podczas pobierania statystyk gatunków"}), 500


@genres_bp.route("/dashboard", methods=["GET"])
@staff_required
def get_genres_dashboard():
    """Pobiera dane dashboard dla gatunków"""
    try:
        dashboard_data = get_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        return jsonify({"error": "Błąd podczas pobierania dashboard gatunków"}), 500
