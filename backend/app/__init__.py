from flask import Flask
from flask_cors import CORS
from app.services.database import db
from flask_jwt_extended import JWTManager
from flask import jsonify

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}}, expose_headers=["Authorization"])
    
    # Konfiguracja
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:ZelseeH2001@localhost:5432/filmhive'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Konfiguracja JWT
    app.config["JWT_SECRET_KEY"] = "7d946d165f6b4c0c3290fa659403bd2d6db51bc95d64328a8d874aed8c481ec8"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # Token ważny przez 24 godziny (w sekundach)
    jwt = JWTManager(app)
    
    # Dodaj obsługę błędów JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Nieprawidłowy token',
            'message': str(error)
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token wygasł',
            'message': 'Token wygasł, zaloguj się ponownie'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Brak tokenu autoryzacyjnego',
            'message': str(error)
        }), 401
    
    # Inicjalizacja rozszerzeń
    db.init_app(app)
    
    # Rejestracja blueprintów
    from app.routes.genres import genres_bp
    from app.routes.movies import movies_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(genres_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.after_request
    def add_charset(response):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    
    return app
