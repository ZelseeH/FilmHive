from flask import Blueprint, jsonify, request, current_app, make_response
from app.services.director_service import DirectorService
from app.services.auth_service import staff_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime

directors_bp = Blueprint("directors", __name__)
director_service = DirectorService()


def cors_headers(f):
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            response = make_response()
        else:
            response = make_response(f(*args, **kwargs))

        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    decorated_function.__name__ = f.__name__
    return decorated_function


@directors_bp.route("/", methods=["GET", "OPTIONS"])
@cors_headers
def get_all_directors():
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = director_service.get_all_directors(page, per_page)
    return jsonify(result)


@directors_bp.route("/<int:director_id>", methods=["GET", "OPTIONS"])
@cors_headers
def get_director(director_id):
    if request.method == "OPTIONS":
        return

    director = director_service.get_director_by_id(director_id)
    if director:
        return jsonify(director.serialize())
    return jsonify({"error": "Director not found"}), 404


@directors_bp.route("/search", methods=["GET", "OPTIONS"])
@cors_headers
def search_directors():
    if request.method == "OPTIONS":
        return

    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = director_service.search_directors(query, page, per_page)
    return jsonify(result)


@directors_bp.route("/", methods=["POST", "OPTIONS"])
@cors_headers
@staff_required
def add_director():
    if request.method == "OPTIONS":
        return

    try:
        director_data = {}

        if request.is_json:
            json_data = request.get_json()
            director_data = {
                "name": json_data.get("name"),
                "birth_date": json_data.get("birth_date"),
                "birth_place": json_data.get("birth_place", ""),
                "biography": json_data.get("biography", ""),
                "gender": json_data.get("gender"),
            }
        else:
            director_data = {
                "name": request.form.get("name"),
                "birth_date": request.form.get("birth_date"),
                "birth_place": request.form.get("birth_place", ""),
                "biography": request.form.get("biography", ""),
                "gender": request.form.get("gender"),
            }

            photo_file = request.files.get("photo")
            if photo_file:
                filename = secure_filename(photo_file.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{filename}"

                upload_dir = os.path.join(current_app.static_folder, "directors")
                os.makedirs(upload_dir, exist_ok=True)

                file_path = os.path.join(upload_dir, filename)
                photo_file.save(file_path)

                director_data["photo_url"] = filename

        director = director_service.add_director(director_data)
        return (
            jsonify(
                {
                    "message": "Reżyser został pomyślnie dodany",
                    "director": director.serialize(),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding director: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas dodawania reżysera", "details": str(e)}
            ),
            500,
        )


@directors_bp.route("/<int:director_id>", methods=["PUT", "OPTIONS"])
@cors_headers
@staff_required
def update_director(director_id):
    if request.method == "OPTIONS":
        return

    try:
        director_data = {}

        if request.is_json:
            json_data = request.get_json()

            if "name" in json_data:
                director_data["name"] = json_data.get("name")
            if "birth_date" in json_data:
                director_data["birth_date"] = json_data.get("birth_date")
            if "birth_place" in json_data:
                director_data["birth_place"] = json_data.get("birth_place")
            if "biography" in json_data:
                director_data["biography"] = json_data.get("biography")
            if "gender" in json_data:
                director_data["gender"] = json_data.get("gender")
        else:
            if "name" in request.form:
                director_data["name"] = request.form.get("name")
            if "birth_date" in request.form:
                director_data["birth_date"] = request.form.get("birth_date")
            if "birth_place" in request.form:
                director_data["birth_place"] = request.form.get("birth_place")
            if "biography" in request.form:
                director_data["biography"] = request.form.get("biography")
            if "gender" in request.form:
                director_data["gender"] = request.form.get("gender")

            photo_file = request.files.get("photo")
            if photo_file:
                director = director_service.upload_director_photo(
                    director_id, photo_file
                )
                if not director:
                    return jsonify({"error": "Nie znaleziono reżysera"}), 404

        director = director_service.update_director(director_id, director_data)
        if not director:
            return jsonify({"error": "Nie znaleziono reżysera"}), 404

        return jsonify(
            {
                "message": "Reżyser został pomyślnie zaktualizowany",
                "director": director.serialize(),
            }
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating director: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas aktualizacji reżysera",
                    "details": str(e),
                }
            ),
            500,
        )


@directors_bp.route("/<int:director_id>", methods=["DELETE", "OPTIONS"])
@cors_headers
@staff_required
def delete_director(director_id):
    if request.method == "OPTIONS":
        return

    try:
        result = director_service.delete_director(director_id)
        if result:
            return jsonify({"message": "Reżyser został pomyślnie usunięty"})
        return jsonify({"error": "Nie znaleziono reżysera"}), 404

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting director: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas usuwania reżysera", "details": str(e)}
            ),
            500,
        )


@directors_bp.route("/<int:director_id>/photo", methods=["POST", "OPTIONS"])
@cors_headers
@staff_required
def upload_photo(director_id):
    if request.method == "OPTIONS":
        return

    try:
        if "photo" not in request.files:
            return jsonify({"error": "Nie przesłano pliku"}), 400

        photo_file = request.files["photo"]
        if photo_file.filename == "":
            return jsonify({"error": "Nie wybrano pliku"}), 400

        director = director_service.upload_director_photo(director_id, photo_file)
        if director:
            return jsonify(
                {
                    "message": "Zdjęcie zostało pomyślnie przesłane",
                    "director": director.serialize(),
                }
            )
        return jsonify({"error": "Nie znaleziono reżysera"}), 404

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error uploading photo: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas przesyłania zdjęcia",
                    "details": str(e),
                }
            ),
            500,
        )


@directors_bp.route("/<int:director_id>/movies", methods=["GET", "OPTIONS"])
@cors_headers
def get_director_movies(director_id):
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = director_service.get_director_movies(director_id, page, per_page)
    if result:
        return jsonify(result)
    return jsonify({"error": "Director not found"}), 404


# STATISTICS & DASHBOARD ENDPOINTS


@directors_bp.route("/statistics", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_directors_statistics():
    """Pobiera podstawowe statystyki reżyserów"""
    if request.method == "OPTIONS":
        return

    try:
        stats = director_service.get_basic_statistics()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting directors statistics: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania statystyk reżyserów"}), 500


@directors_bp.route("/dashboard", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_directors_dashboard():
    """Pobiera dane dashboard dla reżyserów"""
    if request.method == "OPTIONS":
        return

    try:
        dashboard_data = director_service.get_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting directors dashboard: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania dashboard reżyserów"}), 500
