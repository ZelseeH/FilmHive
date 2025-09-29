from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comment_service import CommentService
from app.services.auth_service import admin_required, staff_required
import app.services.user_service as user_service_module

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
def delete_comment_enhanced(comment_id):
    """Usuwa komentarz - użytkownik może usunąć swój, staff może usunąć każdy"""
    try:
        user_id = int(get_jwt_identity())

        # Użyj funkcji zamiast klasy
        user = user_service_module.get_user_by_id(user_id)

        is_staff = user and user.get("role", 3) <= 2

        if is_staff:
            result = comment_service.delete_comment_by_staff(comment_id, user_id)
        else:
            result = comment_service.delete_comment(comment_id, user_id)

        if result:
            action = (
                "usunięcie przez staff" if is_staff else "usunięcie przez użytkownika"
            )
            current_app.logger.info(
                f"Użytkownik {user_id} usunął komentarz {comment_id} ({action})"
            )
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

    except ValueError as e:
        current_app.logger.error(f"ValueError w delete_comment: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Błąd w delete_comment: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas usuwania komentarza"}), 500


@comments_bp.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie_comments(movie_id):
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        include_ratings = request.args.get("include_ratings", "true").lower() == "true"

        # Walidacja parametrów sortowania
        valid_sort_fields = ["created_at", "rating"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        result = comment_service.get_movie_comments(
            movie_id, page, per_page, sort_by, sort_order, include_ratings
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
        include_ratings = request.args.get("include_ratings", "true").lower() == "true"

        result = comment_service.get_user_comments(
            user_id, page, per_page, include_ratings
        )
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
        include_rating = request.args.get("include_rating", "true").lower() == "true"
        comment = comment_service.get_comment_by_id(comment_id, include_rating)
        if comment:
            current_app.logger.info(f"Retrieved comment {comment_id}")
            return jsonify(comment), 200
        else:
            return jsonify({"error": "Komentarz nie istnieje"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in get_comment_by_id: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania komentarza"}), 500


@comments_bp.route("/user/<int:movie_id>", methods=["GET"])
@jwt_required()
def get_user_comment_for_movie(movie_id):
    try:
        user_id = int(get_jwt_identity())
        include_rating = request.args.get("include_rating", "true").lower() == "true"
        comment = comment_service.get_user_comment_for_movie(
            user_id, movie_id, include_rating
        )

        if comment:
            current_app.logger.info(
                f"Retrieved user {user_id} comment for movie {movie_id}"
            )
            return jsonify(comment), 200
        else:
            return jsonify({"message": "Komentarz nie istnieje"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in get_user_comment_for_movie: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania komentarza użytkownika"}
            ),
            500,
        )


@comments_bp.route("/movie/<int:movie_id>/with-ratings", methods=["GET"])
def get_movie_comments_with_ratings(movie_id):
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        valid_sort_fields = ["created_at", "rating"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        result = comment_service.get_movie_comments_with_ratings(
            movie_id, page, per_page, sort_by, sort_order
        )
        current_app.logger.info(
            f"Retrieved comments with ratings for movie {movie_id}, page {page}"
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_movie_comments_with_ratings: {str(e)}")
        return (
            jsonify({"error": "Wystąpił błąd podczas pobierania komentarzy z ocenami"}),
            500,
        )


# STAFF MANAGEMENT ENDPOINTS


@comments_bp.route("/all", methods=["GET"])
@staff_required
def get_all_comments():
    """Pobiera wszystkie komentarze w systemie (tylko dla staff)"""
    try:
        # Pobierz parametry z query string
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        search = request.args.get("search", None)
        date_from = request.args.get("date_from", None)
        date_to = request.args.get("date_to", None)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        # Walidacja parametrów sortowania
        valid_sort_fields = ["created_at", "movie_title", "username"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        result = comment_service.get_all_comments_for_staff(
            page=page,
            per_page=per_page,
            search=search,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        current_app.logger.info(f"Staff retrieved all comments, page {page}")
        return jsonify(result), 200

    except ValueError as e:
        current_app.logger.error(f"ValueError in get_all_comments: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in get_all_comments: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania komentarzy"}), 500


@comments_bp.route("/staff/update/<int:comment_id>", methods=["PUT"])
@staff_required
def update_comment_by_staff(comment_id):
    """Aktualizuje komentarz przez staff (bez sprawdzania właściciela)"""
    try:
        staff_user_id = int(
            get_jwt_identity()
        )  # POPRAWIONE - zamiast g.current_user.user_id
        data = request.json
        comment_text = data.get("comment_text")

        if not comment_text:
            return jsonify({"error": "comment_text jest wymagane"}), 400
        if len(comment_text) > 1000:
            return jsonify({"error": "Komentarz nie może przekraczać 1000 znaków"}), 400

        result = comment_service.update_comment_by_staff(
            comment_id, comment_text, staff_user_id
        )

        if result:
            current_app.logger.info(
                f"Staff {staff_user_id} updated comment {comment_id}"
            )
            return jsonify(result), 200
        else:
            return jsonify({"error": "Komentarz nie istnieje"}), 404

    except ValueError as e:
        current_app.logger.error(f"ValueError in update_comment_by_staff: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in update_comment_by_staff: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas aktualizacji komentarza"}), 500


@comments_bp.route("/staff/delete/<int:comment_id>", methods=["DELETE"])
@staff_required
def delete_comment_by_staff(comment_id):
    """Usuwa komentarz przez staff (bez sprawdzania właściciela)"""
    try:
        staff_user_id = int(
            get_jwt_identity()
        )  # POPRAWIONE - zamiast g.current_user.user_id

        result = comment_service.delete_comment_by_staff(comment_id, staff_user_id)

        if result:
            current_app.logger.info(
                f"Staff {staff_user_id} deleted comment {comment_id}"
            )
            return jsonify({"message": "Komentarz został usunięty przez staff"}), 200
        else:
            return jsonify({"error": "Komentarz nie istnieje"}), 404

    except ValueError as e:
        current_app.logger.error(f"ValueError in delete_comment_by_staff: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in delete_comment_by_staff: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas usuwania komentarza"}), 500


@comments_bp.route("/staff/details/<int:comment_id>", methods=["GET"])
@staff_required
def get_comment_details_for_staff(comment_id):
    """Pobiera szczegółowe informacje o komentarzu dla staff"""
    try:
        result = comment_service.get_comment_details_for_staff(comment_id)

        if result:
            staff_user_id = int(
                get_jwt_identity()
            )  # POPRAWIONE - zamiast g.current_user.user_id
            current_app.logger.info(
                f"Staff {staff_user_id} retrieved details for comment {comment_id}"
            )
            return jsonify(result), 200
        else:
            return jsonify({"error": "Komentarz nie istnieje"}), 404

    except Exception as e:
        current_app.logger.error(f"Error in get_comment_details_for_staff: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas pobierania szczegółów komentarza"}
            ),
            500,
        )


# STATISTICS & DASHBOARD ENDPOINTS - dodaj na końcu pliku


@comments_bp.route("/statistics", methods=["GET"])
@staff_required
def get_comments_basic_statistics():
    """Pobiera podstawowe statystyki komentarzy"""
    try:
        stats = comment_service.get_basic_statistics()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting basic statistics: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania statystyk"}), 500


@comments_bp.route("/dashboard", methods=["GET"])
@staff_required
def get_comments_dashboard():
    """Pobiera dane dashboard dla komentarzy"""
    try:
        dashboard_data = comment_service.get_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania danych dashboard"}), 500
