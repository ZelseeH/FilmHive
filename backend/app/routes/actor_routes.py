from flask import Blueprint, jsonify, request, current_app, make_response
from app.services.actor_service import ActorService
from app.services.auth_service import admin_required, staff_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

actors_bp = Blueprint("actors", __name__)
actor_service = ActorService()


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


@actors_bp.route("/", methods=["GET", "OPTIONS"])
@cors_headers
def get_all_actors():
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.get_all_actors(page, per_page)
    return jsonify(result)


@actors_bp.route("/<int:actor_id>", methods=["GET", "OPTIONS"])
@cors_headers
def get_actor(actor_id):
    if request.method == "OPTIONS":
        return

    actor = actor_service.get_actor_by_id(actor_id)
    if actor:
        return jsonify(actor.serialize())
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/search", methods=["GET", "OPTIONS"])
@cors_headers
def search_actors():
    if request.method == "OPTIONS":
        return

    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.search_actors(query, page, per_page)
    return jsonify(result)


@actors_bp.route("/", methods=["POST", "OPTIONS"])
@cors_headers
@staff_required
def add_actor():
    if request.method == "OPTIONS":
        return

    try:
        actor_data = {}

        if request.is_json:
            json_data = request.get_json()
            actor_data = {
                "name": json_data.get("name"),
                "birth_date": json_data.get("birth_date"),
                "birth_place": json_data.get("birth_place", ""),
                "biography": json_data.get("biography", ""),
                "gender": json_data.get("gender"),
            }
        else:
            actor_data = {
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

                upload_dir = os.path.join(current_app.static_folder, "actors")
                os.makedirs(upload_dir, exist_ok=True)

                file_path = os.path.join(upload_dir, filename)
                photo_file.save(file_path)

                actor_data["photo_url"] = filename

        actor = actor_service.add_actor(actor_data)
        return (
            jsonify(
                {"message": "Aktor został pomyślnie dodany", "actor": actor.serialize()}
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding actor: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas dodawania aktora", "details": str(e)}
            ),
            500,
        )


@actors_bp.route("/<int:actor_id>", methods=["PUT", "OPTIONS"])
@cors_headers
@staff_required
def update_actor(actor_id):
    if request.method == "OPTIONS":
        return

    try:
        actor_data = {}

        if request.is_json:
            json_data = request.get_json()

            if "name" in json_data:
                actor_data["name"] = json_data.get("name")
            if "birth_date" in json_data:
                actor_data["birth_date"] = json_data.get("birth_date")
            if "birth_place" in json_data:
                actor_data["birth_place"] = json_data.get("birth_place")
            if "biography" in json_data:
                actor_data["biography"] = json_data.get("biography")
            if "gender" in json_data:
                actor_data["gender"] = json_data.get("gender")
        else:
            if "name" in request.form:
                actor_data["name"] = request.form.get("name")
            if "birth_date" in request.form:
                actor_data["birth_date"] = request.form.get("birth_date")
            if "birth_place" in request.form:
                actor_data["birth_place"] = request.form.get("birth_place")
            if "biography" in request.form:
                actor_data["biography"] = request.form.get("biography")
            if "gender" in request.form:
                actor_data["gender"] = request.form.get("gender")

            photo_file = request.files.get("photo")
            if photo_file:
                actor = actor_service.upload_actor_photo(actor_id, photo_file)
                if not actor:
                    return jsonify({"error": "Nie znaleziono aktora"}), 404

        actor = actor_service.update_actor(actor_id, actor_data)
        if not actor:
            return jsonify({"error": "Nie znaleziono aktora"}), 404

        return jsonify(
            {
                "message": "Aktor został pomyślnie zaktualizowany",
                "actor": actor.serialize(),
            }
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating actor: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas aktualizacji aktora",
                    "details": str(e),
                }
            ),
            500,
        )


@actors_bp.route("/<int:actor_id>", methods=["DELETE", "OPTIONS"])
@cors_headers
@staff_required
def delete_actor(actor_id):
    if request.method == "OPTIONS":
        return

    try:
        result = actor_service.delete_actor(actor_id)
        if result:
            return jsonify({"message": "Aktor został pomyślnie usunięty"})
        return jsonify({"error": "Nie znaleziono aktora"}), 404

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting actor: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas usuwania aktora", "details": str(e)}
            ),
            500,
        )


@actors_bp.route("/<int:actor_id>/photo", methods=["POST", "OPTIONS"])
@cors_headers
@staff_required
def upload_photo(actor_id):
    if request.method == "OPTIONS":
        return

    try:
        if "photo" not in request.files:
            return jsonify({"error": "Nie przesłano pliku"}), 400

        photo_file = request.files["photo"]
        if photo_file.filename == "":
            return jsonify({"error": "Nie wybrano pliku"}), 400

        actor = actor_service.upload_actor_photo(actor_id, photo_file)
        if actor:
            return jsonify(
                {
                    "message": "Zdjęcie zostało pomyślnie przesłane",
                    "actor": actor.serialize(),
                }
            )
        return jsonify({"error": "Nie znaleziono aktora"}), 404

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


@actors_bp.route("/<int:actor_id>/movies", methods=["GET", "OPTIONS"])
@cors_headers
def get_actor_movies(actor_id):
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = actor_service.get_actor_movies(actor_id, page, per_page)
    if result:
        return jsonify(result)
    return jsonify({"error": "Actor not found"}), 404


@actors_bp.route("/filter", methods=["GET", "OPTIONS"])
@cors_headers
def filter_actors():
    if request.method == "OPTIONS":
        return

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        per_page = min(per_page, 100)

        filters = {}
        if "name" in request.args:
            filters["name"] = request.args.get("name")
        if "countries" in request.args:
            filters["countries"] = request.args.get("countries")
        if "years" in request.args:
            filters["years"] = request.args.get("years")
        if "gender" in request.args:
            filters["gender"] = request.args.get("gender")

        sort_by = request.args.get("sort_by", "name")
        sort_order = request.args.get("sort_order", "asc")

        valid_sort_fields = ["name", "birth_date"]
        valid_sort_orders = ["asc", "desc"]

        if sort_by not in valid_sort_fields:
            sort_by = "name"
        if sort_order.lower() not in valid_sort_orders:
            sort_order = "asc"

        result = actor_service.filter_actors(
            filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in filter_actors route: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Wystąpił błąd podczas filtrowania aktorów",
                    "details": str(e),
                }
            ),
            500,
        )


@actors_bp.route("/birthplaces", methods=["GET", "OPTIONS"])
@cors_headers
def get_birthplaces():
    if request.method == "OPTIONS":
        return

    birthplaces = actor_service.get_unique_birthplaces()
    return jsonify({"birthplaces": birthplaces})
