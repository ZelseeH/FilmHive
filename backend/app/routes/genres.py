from flask import Blueprint, jsonify, request
from app.models.genre import Genre
from app.services.database import db

genres_bp = Blueprint('genres', __name__)

@genres_bp.route('/genres', methods=['GET'])
def get_genres():
    genres = db.session.query(Genre).all()
    return jsonify([genre.serialize() for genre in genres])

@genres_bp.route('/genres', methods=['POST'])
def add_genre():
    data = request.get_json()
    genre_name = data.get('name')

    if not genre_name:
        return jsonify({"error": "Nazwa gatunku jest wymagana"}), 400

    new_genre = Genre(genre_name=genre_name)
    db.session.add(new_genre)
    db.session.commit()

    return jsonify(new_genre.serialize()), 201

@genres_bp.route('/genres/<int:id>', methods=['DELETE'])
def delete_genre(id):
    genre = Genre.query.get(id)

    if not genre:
        return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404

    db.session.delete(genre)
    db.session.commit()

    return jsonify({"message": f"Gatunek o ID {id} został usunięty"}), 200

@genres_bp.route('/genres/<int:id>', methods=['PUT'])
def update_genre(id):
    data = request.get_json()
    genre_name = data.get('name')

    if not genre_name:
        return jsonify({"error": "Nazwa gatunku jest wymagana"}), 400

    genre = Genre.query.get(id)

    if not genre:
        return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404

    genre.genre_name = genre_name
    db.session.commit()

    return jsonify(genre.serialize()), 200
