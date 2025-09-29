from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comment_reply_service import CommentReplyService
from app.repositories.comment_reply_repository import CommentReplyRepository
import app.services.user_service as user_service_module

comment_replies_bp = Blueprint("comment_replies", __name__)


@comment_replies_bp.route("/api/comments/<int:comment_id>/replies", methods=["POST"])
@jwt_required()
def create_reply(comment_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"success": False, "error": "Brak treści odpowiedzi"}), 400

        if not data["text"].strip():
            return (
                jsonify(
                    {"success": False, "error": "Treść odpowiedzi nie może być pusta"}
                ),
                400,
            )

        result = CommentReplyService.create_reply(
            comment_id=comment_id, reply_user_id=user_id, text=data["text"]
        )

        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/comments/<int:comment_id>/thread", methods=["GET"])
def get_comment_thread(comment_id):
    try:
        result = CommentReplyService.get_thread(comment_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/replies/<int:reply_id>", methods=["PUT"])
@jwt_required()
def update_reply(reply_id):
    try:
        current_app.logger.info(
            f"🔍 DEBUG: Received PUT request for reply_id={reply_id}"
        )

        user_id = get_jwt_identity()
        current_app.logger.info(f"🔍 DEBUG: User ID from JWT={user_id}")

        data = request.get_json()
        current_app.logger.info(f"🔍 DEBUG: Request data={data}")

        if not data or "text" not in data:
            current_app.logger.warning("🔍 DEBUG: No text in payload")
            return (
                jsonify({"success": False, "error": "Brak nowej treści odpowiedzi"}),
                400,
            )

        if not data["text"].strip():
            current_app.logger.warning("🔍 DEBUG: Empty text")
            return (
                jsonify(
                    {"success": False, "error": "Treść odpowiedzi nie może być pusta"}
                ),
                400,
            )

        # Sprawdź czy user jest staff
        user = user_service_module.get_user_by_id(user_id)
        is_staff = user and user.get("role", 3) <= 2

        if is_staff:
            current_app.logger.info(f"🔍 DEBUG: Staff user updating reply")
            result = CommentReplyService.update_reply_by_staff(
                reply_id, user_id, data["text"]
            )
        else:
            current_app.logger.info(f"🔍 DEBUG: Regular user updating own reply")
            result = CommentReplyService.update_reply(reply_id, user_id, data["text"])

        current_app.logger.info(f"🔍 DEBUG: Service result={result}")

        if result["success"]:
            return jsonify(result), 200
        else:
            status_code = 403 if "uprawnień" in result.get("error", "") else 404
            return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"🔍 DEBUG: Exception in update_reply: {e}")
        import traceback

        current_app.logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/replies/<int:reply_id>", methods=["DELETE"])
@jwt_required()
def delete_reply(reply_id):
    try:
        current_app.logger.info(
            f"🔍 DEBUG: Received DELETE request for reply_id={reply_id}"
        )

        user_id = get_jwt_identity()
        current_app.logger.info(f"🔍 DEBUG: User ID from JWT={user_id}")

        # Sprawdź czy user jest staff
        user = user_service_module.get_user_by_id(user_id)
        is_staff = user and user.get("role", 3) <= 2

        if is_staff:
            current_app.logger.info(f"🔍 DEBUG: Staff user deleting reply")
            result = CommentReplyService.delete_reply_by_staff(reply_id, user_id)
        else:
            current_app.logger.info(f"🔍 DEBUG: Regular user deleting own reply")
            result = CommentReplyService.delete_reply(reply_id, user_id)

        current_app.logger.info(f"🔍 DEBUG: Service result={result}")

        if result["success"]:
            return jsonify(result), 200
        else:
            status_code = 403 if "uprawnień" in result.get("error", "") else 404
            return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"🔍 DEBUG: Exception in delete_reply: {e}")
        import traceback

        current_app.logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/comments/<int:comment_id>/replies", methods=["GET"])
def get_replies_only(comment_id):
    try:
        replies = CommentReplyRepository.get_with_ratings(comment_id)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "replies": replies,
                        "replies_count": len(replies),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/comments/<int:comment_id>/stats", methods=["GET"])
def get_reply_stats(comment_id):
    try:
        participants = CommentReplyRepository.get_participants(comment_id)
        replies = CommentReplyRepository.get_by_comment(comment_id)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "replies_count": len(replies),
                        "participants_count": len(participants),
                        "participants": participants,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/comments/<int:comment_id>/preview", methods=["GET"])
def get_reply_preview(comment_id):
    try:
        replies = CommentReplyRepository.get_with_ratings(comment_id)
        first_reply = replies[0] if replies else None

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "first_reply": first_reply,
                        "replies_count": len(replies),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


# STAFF MANAGEMENT ENDPOINTS


@comment_replies_bp.route("/api/staff/replies/<int:reply_id>", methods=["PUT"])
@jwt_required()
def update_reply_by_staff(reply_id):
    """Staff może edytować wszystkie odpowiedzi"""
    try:
        staff_user_id = get_jwt_identity()

        # Sprawdź uprawnienia staff
        user = user_service_module.get_user_by_id(staff_user_id)
        if not user or user.get("role", 3) > 2:
            return jsonify({"success": False, "error": "Brak uprawnień staff"}), 403

        data = request.get_json()

        if not data or "text" not in data:
            return (
                jsonify({"success": False, "error": "Brak nowej treści odpowiedzi"}),
                400,
            )

        if not data["text"].strip():
            return (
                jsonify(
                    {"success": False, "error": "Treść odpowiedzi nie może być pusta"}
                ),
                400,
            )

        result = CommentReplyService.update_reply_by_staff(
            reply_id, staff_user_id, data["text"]
        )

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        current_app.logger.error(f"Error in update_reply_by_staff: {e}")
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500


@comment_replies_bp.route("/api/staff/replies/<int:reply_id>", methods=["DELETE"])
@jwt_required()
def delete_reply_by_staff(reply_id):
    """Staff może usuwać wszystkie odpowiedzi"""
    try:
        staff_user_id = get_jwt_identity()

        # Sprawdź uprawnienia staff
        user = user_service_module.get_user_by_id(staff_user_id)
        if not user or user.get("role", 3) > 2:
            return jsonify({"success": False, "error": "Brak uprawnień staff"}), 403

        result = CommentReplyService.delete_reply_by_staff(reply_id, staff_user_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        current_app.logger.error(f"Error in delete_reply_by_staff: {e}")
        return jsonify({"success": False, "error": "Wystąpił błąd serwera"}), 500
