from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
)
from datetime import datetime, timedelta
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.database import db
from app.services.user_service import change_user_password
from app.schemas.user_schema import UserSchema

auth_bp = Blueprint("auth", __name__)
user_repo = UserRepository(db.session)
user_schema = UserSchema()


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
        access_token = create_access_token(
            identity=str(new_user.user_id),
            additional_claims={"role": new_user.role},
            expires_delta=timedelta(days=1),
        )
        return (
            jsonify(
                {
                    "message": "Rejestracja zakończona pomyślnie",
                    "access_token": access_token,
                    "user": user_schema.dump(new_user),
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

    user.last_login = datetime.utcnow()
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role},
        expires_delta=timedelta(days=1),
    )

    return (
        jsonify(
            {
                "message": "Logowanie zakończone pomyślnie",
                "access_token": access_token,
                "user": user_schema.dump(user),
            }
        ),
        200,
    )


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

        return (
            jsonify({"message": "Token jest ważny", "user": user_schema.dump(user)}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_current_user():
    try:
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = user_repo.get_by_id(user_id)
        return user
    except Exception:
        return None


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = user_repo.get_by_id(user_id)
            if not user:
                return jsonify({"error": "Użytkownik nie znaleziony"}), 401
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function


def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = user_repo.get_by_id(user_id)
            if not user or user.role != 1:  # Poprawka: admin to role == 1
                return jsonify({"error": "Wymagane uprawnienia administratora"}), 403
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function
