from flask import Blueprint, jsonify
from app.models.movie import Movie
from app.services.database import db

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    movies = db.session.query(Movie).all()
    return jsonify([movie.serialize() for movie in movies])

@movies_bp.route('/movies/<int:id>', methods=['GET'])
def get_movie(id):
    movie = db.session.get(Movie, id)
    
    if not movie:
        return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
        
    return jsonify(movie.serialize())

@movies_bp.route('/test_db', methods=['GET'])
def test_db():
    try:
        # Próba wykonania prostego zapytania
        result = db.session.execute(db.text("SELECT 1")).fetchone()
        if result:
            return jsonify({"message": "Połączenie z bazą danych działa poprawnie!", "result": result[0]})
        else:
            return jsonify({"error": "Brak wyników zapytania"}), 500
    except Exception as e:
        return jsonify({"error": f"Błąd połączenia z bazą danych: {str(e)}"}), 500
@movies_bp.route('/tables', methods=['GET'])
def list_tables():
    try:
        result = db.session.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).fetchall()
        tables = [row[0] for row in result]
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500