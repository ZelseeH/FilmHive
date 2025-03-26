from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import url_for

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
CORS(app)  # Umożliwia komunikację z serwerem z innych domen
@app.after_request
def add_charset(response):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

# Konfiguracja połączenia z bazą danych PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:ZelseeH2001@localhost:5432/filmhive'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja SQLAlchemy
db = SQLAlchemy(app)

# Model gatunków (Genre)
class Genre(db.Model):
    __tablename__ = 'genres'
    genre_id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(255), nullable=False)

    def serialize(self):
        return {
            "id": self.genre_id,
            "name": self.genre_name
        }

# Endpoint do pobierania wszystkich gatunków
@app.route('/genres', methods=['GET'])
def get_genres():
    genres = Genre.query.all()
    return jsonify([genre.serialize() for genre in genres])

# Endpoint do dodawania nowego gatunku
@app.route('/genres', methods=['POST'])
def add_genre():
    data = request.get_json()
    genre_name = data.get('name')

    if not genre_name:
        return jsonify({"error": "Nazwa gatunku jest wymagana"}), 400

    new_genre = Genre(genre_name=genre_name)
    db.session.add(new_genre)
    db.session.commit()

    return jsonify(new_genre.serialize()), 201

# Endpoint do usuwania istniejącego gatunku
@app.route('/genres/<int:id>', methods=['DELETE'])
def delete_genre(id):
    genre = Genre.query.get(id)

    if not genre:
        return jsonify({"error": "Gatunek o podanym ID nie istnieje"}), 404

    db.session.delete(genre)
    db.session.commit()

    return jsonify({"message": f"Gatunek o ID {id} został usunięty"}), 200

# Endpoint do edytowania nazwy istniejącego gatunku
@app.route('/genres/<int:id>', methods=['PUT'])
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


# Model filmów (Movie)
class Movie(db.Model):
    __tablename__ = 'movies'
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(255))
    duration_minutes = db.Column(db.Integer)
    country = db.Column(db.String(100))
    original_language = db.Column(db.String(100))

    def serialize(self):
        return {
            "id": self.movie_id,
            "title": self.title,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "description": self.description,
            "poster_url": url_for('static', filename=f'posters/{self.poster_url}', _external=True) if self.poster_url else None,
            "duration_minutes": self.duration_minutes,
            "country": self.country,
            "original_language": self.original_language
        }
# Endpoint do pobierania wszystkich filmów
@app.route('/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return jsonify([movie.serialize() for movie in movies])

# Endpoint do pobierania szczegółów konkretnego filmu
@app.route('/movies/<int:id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get(id)
    
    if not movie:
        return jsonify({"error": "Film o podanym ID nie istnieje"}), 404
        
    return jsonify(movie.serialize())


# Uruchomienie serwera
if __name__ == '__main__':
    app.run(debug=True)
