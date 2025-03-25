from flask import Flask
from flask_cors import CORS
from app.services.database import db

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Konfiguracja
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:ZelseeH2001@localhost:5432/filmhive'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicjalizacja rozszerzeń
    db.init_app(app)
    
    # Rejestracja blueprintów
    from app.routes.genres import genres_bp
    from app.routes.movies import movies_bp
    
    app.register_blueprint(genres_bp)
    app.register_blueprint(movies_bp)
    
    @app.after_request
    def add_charset(response):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    
    return app
