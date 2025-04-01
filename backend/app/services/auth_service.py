from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.repositories.user_repository import UserRepository
from app.services.database import db

user_repo = UserRepository(db.session)


def get_current_user():
    """Pobiera aktualnie zalogowanego użytkownika na podstawie tokenu JWT."""
    try:
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = user_repo.get_by_id(user_id)
        return user
    except Exception:
        return None


def login_required(f):
    """Dekorator sprawdzający, czy użytkownik jest zalogowany."""

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
    """Dekorator sprawdzający, czy użytkownik jest administratorem."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = user_repo.get_by_id(user_id)

            if not user or user.role != "admin":
                return jsonify({"error": "Wymagane uprawnienia administratora"}), 403

            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function
