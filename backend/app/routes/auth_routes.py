from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from datetime import datetime, timedelta
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.database import db
from app.services.user_service import change_user_password
import re
import random

auth_bp = Blueprint("auth", __name__)
user_repo = UserRepository(db.session)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not all(key in data for key in ["username", "email", "password"]):
        return (
            jsonify(
                {"error": "Brakujące dane: wymagane są username, email i password"}
            ),
            400,
        )

    if user_repo.get_by_username_or_email(data["username"]):
        return jsonify({"error": "Nazwa użytkownika jest już zajęta"}), 409

    if user_repo.get_by_username_or_email(data["email"]):
        return jsonify({"error": "Email jest już używany"}), 409

    new_user = User(
        username=data["username"],
        email=data["email"],
        registration_date=datetime.utcnow(),
    )
    new_user.set_password(data["password"])

    try:
        user_repo.add(new_user)

        # Krótszy czas życia tokenu dostępowego
        access_token = create_access_token(
            identity=str(new_user.user_id),
            additional_claims={"role": new_user.role},
            expires_delta=timedelta(minutes=30),  # Krótszy czas życia
        )

        # Dodajemy refresh token
        refresh_token = create_refresh_token(
            identity=str(new_user.user_id),
            expires_delta=timedelta(days=30),  # Dłuższy czas życia
        )

        return (
            jsonify(
                {
                    "message": "Rejestracja zakończona pomyślnie",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": new_user.serialize(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not all(key in data for key in ["username", "password"]):
        return (
            jsonify({"error": "Brakujące dane: wymagane są username i password"}),
            400,
        )

    user = user_repo.get_by_username_or_email(data["username"])

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Nieprawidłowa nazwa użytkownika lub hasło"}), 401

    # Sprawdź, czy konto jest aktywne
    if not user.is_active:
        return (
            jsonify({"error": "Konto zostało zawieszone. "}),
            403,
        )

    user.last_login = datetime.utcnow()
    db.session.commit()

    # Krótszy czas życia tokenu dostępowego
    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role},
        expires_delta=timedelta(minutes=30),  # Krótszy czas życia
    )

    # Dodajemy refresh token
    refresh_token = create_refresh_token(
        identity=str(user.user_id),
        expires_delta=timedelta(days=30),  # Dłuższy czas życia
    )

    return (
        jsonify(
            {
                "message": "Logowanie zakończone pomyślnie",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.serialize(),
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Endpoint do odświeżania tokenu dostępowego"""
    try:
        user_id = int(get_jwt_identity())
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        # Tworzenie nowego tokenu dostępowego z aktualną rolą z bazy danych
        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role},
            expires_delta=timedelta(minutes=30),
        )

        return jsonify({"access_token": access_token, "user": user.serialize()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or "current_password" not in data or "new_password" not in data:
            return (
                jsonify(
                    {"error": "Brakujące dane: wymagane są obecne hasło i nowe hasło"}
                ),
                400,
            )

        result = change_user_password(
            user_id, data["current_password"], data["new_password"]
        )

        if not result:
            return jsonify({"error": "Nieprawidłowe obecne hasło"}), 401

        return jsonify({"message": "Hasło zostało zmienione pomyślnie"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Wystąpił nieoczekiwany błąd"}), 500


@auth_bp.route("/verify-token", methods=["GET"])
@jwt_required()
def verify_token():
    try:
        user_id = int(get_jwt_identity())
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        return jsonify({"message": "Token jest ważny", "user": user.serialize()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GOOGLE OAUTH ENDPOINTS


@auth_bp.route("/google", methods=["GET"])
def google_login():
    """Przekierowanie do Google OAuth"""
    try:
        oauth = current_app.oauth  # Pobierz oauth z current_app
        redirect_uri = url_for("auth.google_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        return (
            jsonify({"error": f"Błąd podczas przekierowania do Google: {str(e)}"}),
            500,
        )


@auth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    """Callback po autoryzacji Google"""
    try:
        oauth = current_app.oauth  # Pobierz oauth z current_app
        # Pobierz token z Google
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")

        if not user_info:
            return redirect("http://localhost:3000/login?error=no_user_info")

        # Obsłuż użytkownika OAuth
        result = handle_oauth_user(user_info, "google", user_info.get("sub"))
        return result

    except Exception as e:
        print(f"Google callback error: {str(e)}")
        return redirect("http://localhost:3000/login?error=oauth_failed")


def handle_oauth_user(user_info, provider, provider_id):
    """Obsługuje logowanie/rejestrację użytkownika OAuth"""
    try:
        # Sprawdź czy użytkownik już istnieje po Google ID
        user = user_repo.get_by_google_id(provider_id)

        if not user:
            # Sprawdź czy istnieje użytkownik z tym emailem
            user = user_repo.get_by_username_or_email(user_info.get("email"))

            if user:
                # Połącz istniejące konto z Google OAuth
                user.google_id = provider_id
                if not user.oauth_provider:
                    user.oauth_provider = provider
                db.session.commit()
            else:
                # Utwórz nowego użytkownika
                username = generate_unique_username(
                    user_info.get("name", user_info.get("email"))
                )

                user = User(
                    username=username,
                    email=user_info.get("email"),
                    name=user_info.get("name"),
                    profile_picture=user_info.get("picture"),
                    google_id=provider_id,
                    oauth_provider=provider,
                    oauth_created=True,
                    password_hash=None,  # Brak hasła dla OAuth
                    registration_date=datetime.utcnow(),
                    is_active=True,
                    role=3,  # Domyślna rola użytkownika
                )

                user_repo.add(user)

        # Aktualizuj ostatnie logowanie
        user.update_last_login()
        db.session.commit()

        # Generuj tokeny JWT
        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role},
            expires_delta=timedelta(minutes=30),
        )

        refresh_token = create_refresh_token(
            identity=str(user.user_id), expires_delta=timedelta(days=30)
        )

        # Przekieruj z tokenami na frontend
        return redirect(
            f"http://localhost:3000/auth/success?token={access_token}&refresh={refresh_token}"
        )

    except Exception as e:
        print(f"Handle OAuth user error: {str(e)}")
        db.session.rollback()
        return redirect("http://localhost:3000/login?error=oauth_processing_failed")


def generate_unique_username(base_name):
    """Generuje unikalną nazwę użytkownika"""
    if not base_name:
        base_name = "user"

    # Wyczyść nazwę - usuń znaki specjalne, spacje itp.
    clean_name = re.sub(r"[^a-zA-Z0-9]", "", base_name.lower())
    if not clean_name:
        clean_name = "user"

    # Sprawdź czy nazwa jest dostępna
    username = clean_name
    counter = 1

    while user_repo.get_by_username_or_email(username):
        username = f"{clean_name}{counter}"
        counter += 1

        if counter > 1000:  # Zabezpieczenie
            username = f"{clean_name}{random.randint(1000, 9999)}"
            break

    return username


# Test endpoint
@auth_bp.route("/oauth/test", methods=["GET"])
def oauth_test():
    """Test endpoint dla OAuth"""
    try:
        oauth = current_app.oauth
        return jsonify(
            {
                "message": "OAuth endpoints are ready",
                "available_providers": ["google"],
                "google_configured": bool(oauth.google),
            }
        )
    except Exception as e:
        return jsonify(
            {
                "message": "OAuth configuration error",
                "error": str(e),
                "available_providers": [],
                "google_configured": False,
            }
        )
