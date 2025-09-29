from flask import Blueprint, request, jsonify
from app.services.database import db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import admin_required, staff_required
from app.models.user import User
from app.services.user_activity_service import (
    log_role_change,
    log_account_block,
    log_account_unblock,
)

admin_bp = Blueprint("admin", __name__)
user_repo = UserRepository(db.session)


@admin_bp.route("/users", methods=["GET"])
@staff_required
def get_all_users():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search", "")
        role = request.args.get("role", type=int)

        from flask_jwt_extended import get_jwt_identity

        current_user_id = int(get_jwt_identity())

        from app.models.user import User

        query = db.session.query(User)

        # Usunięto filtr wykluczający bieżącego użytkownika
        # query = query.filter(User.user_id != current_user_id)

        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
                )
            )

        if role is not None:
            query = query.filter(User.role == role)

        query = query.order_by(User.role, User.username)
        users = query.paginate(page=page, per_page=per_page)

        # Dodajemy informację o bieżącym użytkowniku do każdego obiektu użytkownika
        serialized_users = []
        for user in users.items:
            user_data = user.serialize()
            user_data["is_current_user"] = user.user_id == current_user_id
            serialized_users.append(user_data)

        return (
            jsonify(
                {
                    "users": serialized_users,
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


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Brak danych do aktualizacji"}), 400

        user = user_repo.get_by_id(user_id)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        from flask_jwt_extended import get_jwt_identity

        current_user_id = int(get_jwt_identity())

        # Walidacja danych
        if "email" in data and not data["email"]:
            return jsonify({"error": "Email nie może być pusty"}), 400

        if "username" in data and not data["username"]:
            return jsonify({"error": "Nazwa użytkownika nie może być pusta"}), 400

        # Sprawdzenie unikalności nazwy użytkownika i emaila
        if "username" in data and data["username"] != user.username:
            existing_user = user_repo.get_by_username(data["username"])
            if existing_user:
                return jsonify({"error": "Nazwa użytkownika jest już zajęta"}), 400

        if "email" in data and data["email"] != user.email:
            existing_user = user_repo.get_by_email(data["email"])
            if existing_user:
                return jsonify({"error": "Email jest już używany"}), 400

        # Aktualizacja pól
        if "username" in data:
            user.username = data["username"]

        if "email" in data:
            user.email = data["email"]

        if "name" in data:
            user.name = data["name"]

        if "bio" in data:
            user.bio = data["bio"]

        if "is_active" in data:
            user.is_active = bool(data["is_active"])

        # Aktualizacja roli (z ograniczeniami)
        if "role" in data:
            new_role = int(data["role"])

            # Sprawdzenie, czy rola jest prawidłowa
            if new_role not in [1, 2, 3]:
                return jsonify({"error": "Nieprawidłowa rola"}), 400

            # Nie można modyfikować własnego konta
            if user_id == current_user_id:
                return (
                    jsonify(
                        {"error": "Nie możesz zmienić roli swojego własnego konta"}
                    ),
                    403,
                )

            # Administrator nie może nadać nikomu roli administratora
            if new_role == 1 and user.role != 1:
                return (
                    jsonify({"error": "Nie możesz nadać nikomu roli administratora"}),
                    403,
                )

            # Administrator nie może odebrać roli administratora innemu administratorowi
            if user.role == 1 and new_role != 1:
                return (
                    jsonify(
                        {
                            "error": "Nie możesz odebrać roli administratora innemu administratorowi"
                        }
                    ),
                    403,
                )

            user.role = new_role

        db.session.commit()

        return (
            jsonify(
                {"message": "Dane użytkownika zaktualizowane", "user": user.serialize()}
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>/password", methods=["PUT"])
@admin_required
def reset_user_password(user_id):
    try:
        data = request.get_json()
        if not data or "password" not in data:
            return jsonify({"error": "Brak nowego hasła"}), 400

        new_password = data["password"]
        if len(new_password) < 8:
            return jsonify({"error": "Hasło musi mieć co najmniej 8 znaków"}), 400

        user = user_repo.get_by_id(user_id)
        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({"message": "Hasło użytkownika zostało zresetowane"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@admin_required
def change_user_role(user_id):
    try:
        data = request.get_json()

        if not data or "role" not in data:
            return jsonify({"error": "Brakujące dane: wymagana jest rola"}), 400

        new_role = int(data["role"])

        if new_role not in [1, 2, 3]:
            return jsonify({"error": "Nieprawidłowa rola"}), 400

        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        from flask_jwt_extended import get_jwt_identity

        current_user_id = int(get_jwt_identity())
        current_user = user_repo.get_by_id(current_user_id)

        if user_id == current_user_id:
            return (
                jsonify({"error": "Nie możesz zmienić roli swojego własnego konta"}),
                403,
            )

        if new_role == 1:
            return (
                jsonify({"error": "Nie możesz nadać nikomu roli administratora"}),
                403,
            )

        if user.role == 1:
            return (
                jsonify(
                    {
                        "error": "Nie możesz odebrać roli administratora innemu administratorowi"
                    }
                ),
                403,
            )

        # 🔥 ZAPISZ STARĄ ROLĘ PRZED ZMIANĄ
        old_role = user.role

        user.role = new_role
        db.session.commit()

        # 🔥 LOGUJ ZMIANĘ ROLI
        log_role_change(user_id, old_role, new_role)

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

        from flask_jwt_extended import get_jwt_identity

        current_user_id = int(get_jwt_identity())

        user.is_active = is_active
        db.session.commit()

        # 🔥 LOGUJ BLOKOWANIE/ODBLOKOWANIE KONTA
        if is_active:
            log_account_unblock(user_id, current_user_id)
        else:
            log_account_block(user_id, current_user_id)

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


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    try:
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({"error": "Użytkownik nie znaleziony"}), 404

        from flask_jwt_extended import get_jwt_identity
        from sqlalchemy import text

        current_user_id = int(get_jwt_identity())

        # Sprawdzenia bezpieczeństwa
        if user_id == current_user_id:
            return jsonify({"error": "Nie możesz usunąć swojego własnego konta"}), 403

        if user.role == 1:
            return (
                jsonify({"error": "Nie możesz usunąć konta innego administratora"}),
                403,
            )

        user_data = user.serialize()

        # KASKADOWE USUWANIE - każde polecenie w osobnej try-except
        try:
            # 1. Usuń ratings
            try:
                result = db.session.execute(
                    text("DELETE FROM ratings WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                print(f"Usunięto {result.rowcount} ocen")
            except Exception as e:
                print(f"Błąd ratings: {e}")
                db.session.rollback()  # Rollback tylko tej operacji

            # 2. Usuń comments
            try:
                result = db.session.execute(
                    text("DELETE FROM comments WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                print(f"Usunięto {result.rowcount} komentarzy")
            except Exception as e:
                print(f"Błąd comments: {e}")
                db.session.rollback()

            # 3. Usuń favorite_movies
            try:
                result = db.session.execute(
                    text("DELETE FROM favorite_movies WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                print(f"Usunięto {result.rowcount} ulubionych")
            except Exception as e:
                print(f"Błąd favorite_movies: {e}")
                db.session.rollback()

            # 4. Usuń watchlist
            try:
                result = db.session.execute(
                    text("DELETE FROM watchlist WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                print(f"Usunięto {result.rowcount} z watchlist")
            except Exception as e:
                print(f"Błąd watchlist: {e}")
                db.session.rollback()

            # 5. Usuń activity_logs
            try:
                result = db.session.execute(
                    text("DELETE FROM activity_logs WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                print(f"Usunięto {result.rowcount} logów aktywności")
            except Exception as e:
                print(f"Błąd activity_logs: {e}")
                db.session.rollback()

            # 6. Usuń login_activities
            try:
                result = db.session.execute(
                    text("DELETE FROM login_activities WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                print(f"Usunięto {result.rowcount} logów logowania")
            except Exception as e:
                print(f"Błąd login_activities: {e}")
                db.session.rollback()

            # 7. Na końcu usuń użytkownika - to MUSI się powieść
            try:
                db.session.execute(
                    text("DELETE FROM users WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                db.session.commit()  # Commit tylko jeśli user został usunięty

                return (
                    jsonify(
                        {
                            "message": "Użytkownik został pomyślnie usunięty",
                            "user": user_data,
                        }
                    ),
                    200,
                )
            except Exception as e:
                db.session.rollback()
                return (
                    jsonify({"error": f"Błąd podczas usuwania użytkownika: {str(e)}"}),
                    500,
                )

        except Exception as delete_error:
            db.session.rollback()
            return (
                jsonify(
                    {"error": f"Ogólny błąd podczas usuwania: {str(delete_error)}"}
                ),
                500,
            )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    try:
        data = request.get_json()

        # Sprawdzenie wymaganych pól
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Pole {field} jest wymagane"}), 400

        # Sprawdzenie unikalności nazwy użytkownika i emaila
        if user_repo.get_by_username(data["username"]):
            return jsonify({"error": "Nazwa użytkownika jest już zajęta"}), 400

        if user_repo.get_by_email(data["email"]):
            return jsonify({"error": "Email jest już używany"}), 400

        # Walidacja hasła
        if len(data["password"]) < 8:
            return jsonify({"error": "Hasło musi mieć co najmniej 8 znaków"}), 400

        # Ustawienie domyślnych wartości
        role = data.get("role", 3)  # Domyślnie zwykły użytkownik
        is_active = data.get("is_active", True)

        # Walidacja roli
        if role not in [1, 2, 3]:
            return jsonify({"error": "Nieprawidłowa rola"}), 400

        # Tworzenie nowego użytkownika
        new_user = User(
            username=data["username"],
            email=data["email"],
            name=data.get("name", ""),
            bio=data.get("bio", ""),
            role=role,
            is_active=is_active,
        )

        # Ustawienie hasła
        new_user.set_password(data["password"])

        # Zapisanie do bazy danych
        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Użytkownik został pomyślnie utworzony",
                    "user": new_user.serialize(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
