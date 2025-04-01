from flask import Blueprint, jsonify, request
from app.services.movie_service import get_all_movies, get_movies_paginated, get_movie_by_id, create_movie, delete_movie

# Tworzenie blueprintu
movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/', methods=['GET'])
def get_movies_list():
    """Zwraca listę filmów z paginacją."""
    try:
        # Sprawdzamy, czy żądanie zawiera parametry paginacji
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        genre_id = request.args.get('genre_id', type=int)
        
        # Ograniczamy liczbę filmów na stronę do maksymalnie 10
        if per_page > 10:
            per_page = 10
        
        # Pobieramy filmy z paginacją
        result = get_movies_paginated(page, per_page, genre_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Wystąpił błąd podczas pobierania filmów", "details": str(e)}), 500

@movies_bp.route('/all', methods=['GET'])
def get_all_movies_list():
    """Zwraca listę wszystkich filmów (bez paginacji)."""
    try:
        movies = get_all_movies()
        return jsonify(movies), 200
    except Exception as e:
        return jsonify({"error": "Wystąpił błąd podczas pobierania filmów", "details": str(e)}), 500

@movies_bp.route('/<int:id>', methods=['GET'])
def get_movie(id):
    """Zwraca szczegóły filmu na podstawie ID."""
    try:
        # Sprawdzamy, czy żądanie zawiera parametr include_roles
        include_roles = request.args.get('include_roles', 'false').lower() == 'true'
        
        movie = get_movie_by_id(id, include_actors_roles=include_roles)
        if not movie:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
        return jsonify(movie), 200
    except Exception as e:
        return jsonify({"error": "Wystąpił błąd podczas pobierania filmu", "details": str(e)}), 500


@movies_bp.route('/', methods=['POST'])
def add_movie():
    """Dodaje nowy film."""
    data = request.get_json()
    
    # Walidacja danych wejściowych
    if not data or 'title' not in data or 'release_date' not in data:
        return jsonify({"error": "Brak wymaganych pól: title i release_date"}), 400
    
    try:
        new_movie = create_movie(data)
        return jsonify(new_movie), 201
    except Exception as e:
        return jsonify({"error": "Wystąpił błąd podczas dodawania filmu", "details": str(e)}), 500

@movies_bp.route('/<int:id>', methods=['DELETE'])
def remove_movie(id):
    """Usuwa film na podstawie ID."""
    try:
        success = delete_movie(id)
        if success:
            return jsonify({"message": "Film został usunięty"}), 200
        else:
            return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
    except Exception as e:
        return jsonify({"error": "Wystąpił błąd podczas usuwania filmu", "details": str(e)}), 500
