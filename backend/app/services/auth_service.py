from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from functools import wraps
from app.repositories.user_repository import UserRepository
from app.services.database import db

user_repo = UserRepository(db.session)


def get_current_user():
    try:
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = user_repo.get_by_id(user_id)
        return user
    except Exception:
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            # Dla operacji administracyjnych zawsze sprawdzamy rolę w bazie danych
            user_id = int(get_jwt_identity())
            user = user_repo.get_by_id(user_id)

            if not user or user.role != 1:  # 1 = admin
                return jsonify({"error": "Wymagane uprawnienia administratora"}), 403

            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function


def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            # Dla operacji moderatorskich zawsze sprawdzamy rolę w bazie danych
            user_id = int(get_jwt_identity())
            user = user_repo.get_by_id(user_id)

            if not user or user.role > 2:  # 1 = admin, 2 = moderator
                return jsonify({"error": "Wymagane uprawnienia moderatora"}), 403

            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function


def staff_required(f):
    """Wymaga uprawnień administratora lub moderatora"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            # Dla operacji personelu zawsze sprawdzamy rolę w bazie danych
            user_id = int(get_jwt_identity())
            user = user_repo.get_by_id(user_id)

            if not user or user.role > 2:  # 1 = admin, 2 = moderator
                return (
                    jsonify(
                        {"error": "Wymagane uprawnienia administratora lub moderatora"}
                    ),
                    403,
                )

            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

    return decorated_function


def role_from_token(required_role=None):
    """Sprawdza rolę z tokenu JWT - szybsza weryfikacja dla niekrytycznych operacji"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                role = claims.get("role", 3)  # Domyślnie zwykły użytkownik (3)

                if required_role is not None and role > required_role:
                    return jsonify({"error": "Niewystarczające uprawnienia"}), 403

                return f(*args, **kwargs)
            except Exception:
                return jsonify({"error": "Wymagane uwierzytelnienie"}), 401

        return decorated_function

    return decorator
