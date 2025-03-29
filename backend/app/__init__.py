from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.services.database import db

def create_app():
    app = Flask(__name__)
    
    # Konfiguracja CORS
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}}, expose_headers=["Authorization"])
    
    # Konfiguracja bazy danych
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:ZAQ!2wsx@localhost:5432/filmhive'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Konfiguracja JWT
    app.config["JWT_SECRET_KEY"] = "7d946d165f6b4c0c3290fa659403bd2d6db51bc95d64328a8d874aed8c481ec8"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # Token ważny przez 24 godziny
    
    # Inicjalizacja rozszerzeń
    jwt = JWTManager(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Obsługa błędów JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Nieprawidłowy token', 'message': str(error)}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token wygasł', 'message': 'Zaloguj się ponownie'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Brak tokenu', 'message': str(error)}), 401

    # Globalne obsługi błędów
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Nie znaleziono zasobu"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Błąd serwera"}), 500

    # Rejestracja tras (blueprints)
    from app.routes.movie_routes import movies_bp  # Blueprint dla filmów
    from app.routes.genre_routes import genres_bp  # Blueprint dla gatunków (poprawiona ścieżka)
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp


    app.register_blueprint(movies_bp, url_prefix='/api/movies')  # Endpointy: /api/movies/...
    app.register_blueprint(genres_bp, url_prefix='/api/genres')  # Endpointy: /api/genres/...
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    # Nagłówek charset
    @app.after_request
    def add_charset(response):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    
    return app
