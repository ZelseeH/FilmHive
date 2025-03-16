from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


# Inicjalizacja aplikacji Flask
app = Flask(__name__)

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

# Uruchomienie serwera
if __name__ == '__main__':
    app.run(debug=True)
