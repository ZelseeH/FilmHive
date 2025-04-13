from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comment_service import CommentService

comments_bp = Blueprint("comments", __name__)
comment_service = CommentService()


@comments_bp.route("/add", methods=["POST"])
@jwt_required()
def add_comment():
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        movie_id = data.get("movie_id")
        comment_text = data.get("comment_text")

        if not movie_id:
            return jsonify({"error": "movie_id jest wymagane"}), 400
        if not comment_text:
            return jsonify({"error": "comment_text jest wymagane"}), 400
        if len(comment_text) > 1000:
            return jsonify({"error": "Komentarz nie może przekraczać 1000 znaków"}), 400

        result = comment_service.add_comment(user_id, movie_id, comment_text)
        current_app.logger.info(f"User {user_id} added comment to movie {movie_id}")
        return jsonify(result), 201
    except ValueError as e:
        current_app.logger.error(f"ValueError in add_comment: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in add_comment: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas dodawania komentarza"}), 500


@comments_bp.route("/update/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        comment_text = data.get("comment_text")

        if not comment_text:
            return jsonify({"error": "comment_text jest wymagane"}), 400
        if len(comment_text) > 1000:
            return jsonify({"error": "Komentarz nie może przekraczać 1000 znaków"}), 400

        result = comment_service.update_comment(comment_id, user_id, comment_text)
        if result:
            current_app.logger.info(f"User {user_id} updated comment {comment_id}")
            return jsonify(result), 200
        else:
            return (
                jsonify(
                    {
                        "error": "Komentarz nie istnieje lub nie masz uprawnień do jego edycji"
                    }
                ),
                404,
            )
    except ValueError as e:
        current_app.logger.error(f"ValueError in update_comment: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in update_comment: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas aktualizacji komentarza"}), 500


@comments_bp.route("/delete/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    try:
        user_id = int(get_jwt_identity())
        result = comment_service.delete_comment(comment_id, user_id)

        if result:
            current_app.logger.info(f"User {user_id} deleted comment {comment_id}")
            return jsonify({"message": "Komentarz został usunięty"}), 200
        else:
            return (
                jsonify(
                    {
                        "error": "Komentarz nie istnieje lub nie masz uprawnień do jego usunięcia"
                    }
                ),
                404,
            )
    except Exception as e:
        current_app.logger.error(f"Error in delete_comment: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas usuwania komentarza"}), 500


@comments_bp.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie_comments(movie_id):
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        # Walidacja parametrów sortowania
        if sort_by not in ["created_at"]:
            sort_by = "created_at"
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        result = comment_service.get_movie_comments(
            movie_id, page, per_page, sort_by, sort_order
        )
        current_app.logger.info(f"Retrieved comments for movie {movie_id}, page {page}")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_movie_comments: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania komentarzy"}), 500


@comments_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_comments():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)

        result = comment_service.get_user_comments(user_id, page, per_page)
        current_app.logger.info(f"Retrieved comments for user {user_id}, page {page}")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user_comments: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania komentarzy użytkownika"}
            ),
            500,
        )


@comments_bp.route("/count/<int:movie_id>", methods=["GET"])
def get_movie_comment_count(movie_id):
    try:
        count = comment_service.count_movie_comments(movie_id)
        current_app.logger.info(
            f"Retrieved comment count for movie {movie_id}: {count}"
        )
        return jsonify({"count": count}), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_movie_comment_count: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas pobierania liczby komentarzy"}),
            500,
        )


@comments_bp.route("/<int:comment_id>", methods=["GET"])
def get_comment_by_id(comment_id):
    try:
        comment = comment_service.get_comment_by_id(comment_id)
        if comment:
            current_app.logger.info(f"Retrieved comment {comment_id}")
            return jsonify(comment), 200
        else:
            return jsonify({"error": "Komentarz nie istnieje"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in get_comment_by_id: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania komentarza"}), 500
