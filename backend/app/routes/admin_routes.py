from flask import Blueprint, request, jsonify
from app.services.database import db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import admin_required, staff_required
from app.models.user import User

admin_bp = Blueprint("admin", __name__)
user_repo = UserRepository(db.session)


@admin_bp.route("/users", methods=["GET"])
@staff_required
def get_all_users():
    """Pobierz listę wszystkich użytkowników (dostępne dla admina i moderatora)"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search", "")
        role = request.args.get("role", type=int)

        # Pobierz ID aktualnie zalogowanego użytkownika
        from flask_jwt_extended import get_jwt_identity

        current_user_id = int(get_jwt_identity())

        # Rozpocznij zapytanie
        from app.models.user import User  # Dodaj import modelu User

        query = db.session.query(User)

        # Wyklucz aktualnie zalogowanego użytkownika z wyników
        query = query.filter(User.user_id != current_user_id)

        # Dodaj filtrowanie po wyszukiwaniu (nazwa użytkownika lub email)
        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
                )
            )

        # Dodaj filtrowanie po roli
        if role is not None:
            query = query.filter(User.role == role)

        # Sortowanie najpierw po roli, potem po nazwie użytkownika
        query = query.order_by(User.role, User.username)

        # Wykonaj paginację
        users = query.paginate(page=page, per_page=per_page)

        return (
            jsonify(
                {
                    "users": [user.serialize() for user in users.items],
                    "pagination": {
                        "page": users.page,
                        "per_page": users.per_page,
                        "total": users.total,
                        "total_pages": users.pages,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@staff_required
def get_user_details(user_id):
    """Pobierz szczegóły użytkownika (dostępne dla admina i moderatora)"""
    try:
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        return (
            jsonify(
                user.serialize(
                    include_ratings=True,
                    include_comments=True,
                    include_activity_logs=True,
                    include_login_activities=True,
                )
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@admin_required  # Zostawiamy admin_required
def change_user_role(user_id):
    """Zmień rolę użytkownika (dostępne tylko dla admina)"""
    try:
        data = request.get_json()

        if not data or "role" not in data:
            return jsonify({"error": "Brakujące dane: wymagana jest rola"}), 400

        new_role = int(data["role"])

        # Sprawdzenie, czy rola jest prawidłowa
        if new_role not in [1, 2, 3]:  # admin, moderator, user
            return jsonify({"error": "Nieprawidłowa rola"}), 400

        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        # Pobierz aktualnego użytkownika (administratora)
        from flask_jwt_extended import get_jwt_identity

        current_user_id = int(get_jwt_identity())
        current_user = user_repo.get_by_id(current_user_id)

        # Nie można modyfikować własnego konta
        if user_id == current_user_id:
            return (
                jsonify({"error": "Nie możesz zmienić roli swojego własnego konta"}),
                403,
            )

        # Administrator nie może nadać nikomu roli administratora
        if new_role == 1:
            return (
                jsonify({"error": "Nie możesz nadać nikomu roli administratora"}),
                403,
            )

        # Administrator nie może odebrać roli administratora innemu administratorowi
        if user.role == 1:
            return (
                jsonify(
                    {
                        "error": "Nie możesz odebrać roli administratora innemu administratorowi"
                    }
                ),
                403,
            )

        # Zmiana roli
        user.role = new_role
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Rola użytkownika zmieniona pomyślnie",
                    "user": user.serialize(),
                }
            ),
            200,
        )
    except ValueError:
        return jsonify({"error": "Nieprawidłowy format danych"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@admin_required
def change_user_status(user_id):
    """Aktywuj/dezaktywuj konto użytkownika (dostępne tylko dla admina)"""
    try:
        data = request.get_json()

        if not data or "is_active" not in data:
            return (
                jsonify({"error": "Brakujące dane: wymagany jest status aktywności"}),
                400,
            )

        is_active = bool(data["is_active"])

        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        user.is_active = is_active
        db.session.commit()

        status_text = "aktywowane" if is_active else "dezaktywowane"

        return (
            jsonify(
                {
                    "message": f"Konto użytkownika zostało {status_text}",
                    "user": user.serialize(),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_admin_stats():
    """Pobierz statystyki dla panelu administratora (dostępne tylko dla admina)"""
    try:

        total_users = user_repo.count_all()
        active_users = user_repo.count_active()
        admins = user_repo.count_by_role(1)
        moderators = user_repo.count_by_role(2)

        return (
            jsonify(
                {
                    "users": {
                        "total": total_users,
                        "active": active_users,
                        "admins": admins,
                        "moderators": moderators,
                    }
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
