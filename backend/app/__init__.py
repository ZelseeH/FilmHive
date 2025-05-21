from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from app.extensions import db

load_dotenv(".env")

# Inicjalizacja SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    CORS(
        app,
        resources={r"/api/*": {"origins": "*", "supports_credentials": True}},
        expose_headers=["Authorization"],
    )

    # Konfiguracja bazy danych
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg2://postgres:ZAQ!2wsx@localhost:5432/filmhive"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400

    # Inicjalizacja rozszerzeń
    from app.extensions import db, migrate, jwt

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        # Import modeli PO inicjalizacji db
        from app.models.actor import Actor
        from app.models.director import Director

        db.create_all()

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Nieprawidłowy token", "message": str(error)}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"error": "Token wygasł", "message": "Zaloguj się ponownie"}),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Brak tokenu", "message": str(error)}), 401

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Nie znaleziono zasobu"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Błąd serwera"}), 500

    from app.routes.movie_routes import movies_bp
    from app.routes.genre_routes import genres_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.rating_routes import ratings_bp
    from app.routes.actor_routes import actors_bp
    from app.routes.favorite_movie_routes import favorites_bp
    from app.routes.watchlist_routes import watchlist_bp
    from app.routes.comment_routes import comments_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.people_routes import people_bp
    from app.routes.director_routes import directors_bp

    app.register_blueprint(movies_bp, url_prefix="/api/movies")
    app.register_blueprint(genres_bp, url_prefix="/api/genres")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(ratings_bp, url_prefix="/api/ratings")
    app.register_blueprint(actors_bp, url_prefix="/api/actors")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")
    app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")
    app.register_blueprint(comments_bp, url_prefix="/api/comments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(ai_bp)
    app.register_blueprint(people_bp, url_prefix="/api/people")
    app.register_blueprint(directors_bp, url_prefix="/api/directors")

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            return "", 200

    @app.after_request
    def add_charset(response):
        if response.mimetype == "application/json":
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react_app(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")

    return app
