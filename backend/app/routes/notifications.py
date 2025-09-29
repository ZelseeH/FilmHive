from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/api/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    """Pobiera powiadomienia użytkownika"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get("limit", 50, type=int)
        include_movie = request.args.get("include_movie", "true").lower() == "true"

        if limit > 100:
            limit = 100

        result = NotificationService.get_user_notifications(
            user_id, limit, include_movie
        )

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route("/api/notifications/unread", methods=["GET"])
@jwt_required()
def get_unread_notifications():
    """Pobiera nieprzeczytane powiadomienia"""
    try:
        user_id = get_jwt_identity()

        result = NotificationService.get_unread_notifications(user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route("/api/notifications/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    """Pobiera liczbę nieprzeczytanych powiadomień"""
    try:
        user_id = get_jwt_identity()
        count = NotificationService.get_unread_count(user_id)

        return jsonify({"unread_count": count}), 200

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route(
    "/api/notifications/<int:notification_id>/read", methods=["POST"]
)
@jwt_required()
def mark_notification_read(notification_id):
    """Oznacza powiadomienie jako przeczytane"""
    try:
        user_id = get_jwt_identity()

        result = NotificationService.mark_notification_as_read(notification_id, user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route(
    "/api/notifications/<int:notification_id>/click", methods=["POST"]
)
@jwt_required()
def click_notification(notification_id):
    """Obsługuje kliknięcie w powiadomienie - oznacza jako przeczytane i zwraca dane do przekierowania"""
    try:
        user_id = get_jwt_identity()

        # Pobierz powiadomienie
        notification = NotificationRepository.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Powiadomienie nie istnieje lub nie należy do użytkownika",
                    }
                ),
                404,
            )

        # Oznacz jako przeczytane (jeśli nie było)
        if not notification.is_read:
            NotificationService.mark_notification_as_read(notification_id, user_id)

        # Zwróć dane do przekierowania
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Powiadomienie odczytane",
                    "redirect_url": notification.get_movie_url(),
                    "movie_id": notification.get_movie_id(),
                    "comment_id": notification.comment_id,
                    "reply_id": notification.reply_id,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route("/api/notifications/read-all", methods=["POST"])
@jwt_required()
def mark_all_notifications_read():
    """Oznacza wszystkie powiadomienia jako przeczytane"""
    try:
        user_id = get_jwt_identity()

        result = NotificationService.mark_all_as_read(user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route("/api/notifications/stats", methods=["GET"])
@jwt_required()
def get_notification_stats():
    """Pobiera statystyki powiadomień użytkownika"""
    try:
        user_id = get_jwt_identity()

        result = NotificationService.get_notification_stats(user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route("/api/notifications/comment/<int:comment_id>", methods=["GET"])
@jwt_required()
def get_notifications_by_comment(comment_id):
    """Pobiera powiadomienia dla konkretnego komentarza"""
    try:
        notifications = NotificationService.get_by_comment(comment_id)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "notifications": notifications,
                        "count": len(notifications),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@notifications_bp.route("/api/notifications/create", methods=["POST"])
@jwt_required()
def create_notification():
    """Tworzy nowe powiadomienie"""
    try:
        data = request.get_json()

        required_fields = ["user_id", "message"]
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        from_user_id = get_jwt_identity()

        result = NotificationService.create_notification(
            user_id=data["user_id"],
            from_user_id=from_user_id,
            message=data["message"],
            comment_id=data.get("comment_id"),
            reply_id=data.get("reply_id"),
        )

        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500
