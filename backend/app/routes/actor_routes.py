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
                "photo_url": json_data.get("photo_url"),  # Dodaj photo_url z JSON
            }
        else:
            # FormData request
            actor_data = {
                "name": request.form.get("name"),
                "birth_date": request.form.get("birth_date"),
                "birth_place": request.form.get("birth_place", ""),
                "biography": request.form.get("biography", ""),
                "gender": request.form.get("gender"),
            }

            # POPRAWKA: Obsługa photo_url z formularza
            photo_url_from_form = request.form.get("photo_url")
            if photo_url_from_form and photo_url_from_form.strip():
                # Użytkownik podał URL
                actor_data["photo_url"] = photo_url_from_form.strip()
                current_app.logger.info(
                    f"🔗 Otrzymano photo_url z formularza: {photo_url_from_form}"
                )

            # Obsługa pliku (jeśli nie ma URL-a)
            elif "photo" in request.files:
                photo_file = request.files.get("photo")
                if photo_file and photo_file.filename:
                    filename = secure_filename(photo_file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{timestamp}_{filename}"

                    upload_dir = os.path.join(current_app.static_folder, "actors")
                    os.makedirs(upload_dir, exist_ok=True)

                    file_path = os.path.join(upload_dir, filename)
                    photo_file.save(file_path)

                    actor_data["photo_url"] = filename  # Zapisz nazwę pliku
                    current_app.logger.info(f"📁 Uploadowano plik: {filename}")

        # DEBUG: Wyloguj wszystkie dane przed wysłaniem do service
        current_app.logger.info(f"📋 Dane aktora do utworzenia: {actor_data}")

        # DEBUG: Sprawdź co jest w request
        current_app.logger.info(f"🔍 Request form keys: {list(request.form.keys())}")
        current_app.logger.info(f"🔍 Request files keys: {list(request.files.keys())}")
        if "photo_url" in request.form:
            current_app.logger.info(
                f"🔍 photo_url w formularzu: '{request.form.get('photo_url')}'"
            )

        actor = actor_service.add_actor(actor_data)

        # DEBUG: Sprawdź co zostało zapisane
        current_app.logger.info(
            f"✅ Utworzono aktora: {actor.actor_name}, photo_url: {actor.photo_url}"
        )

        return (
            jsonify(
                {"message": "Aktor został pomyślnie dodany", "actor": actor.serialize()}
            ),
            201,
        )

    except ValueError as e:
        current_app.logger.error(f"❌ Błąd walidacji: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"❌ Unexpected error adding actor: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas dodawania aktora", "details": str(e)}
            ),
            500,
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

        # DEBUG: Sprawdź co przychodzi
        current_app.logger.info(f"🔍 Update actor {actor_id}")
        current_app.logger.info(f"🔍 Content-Type: {request.content_type}")
        current_app.logger.info(f"🔍 Form keys: {list(request.form.keys())}")
        current_app.logger.info(f"🔍 Files keys: {list(request.files.keys())}")

        if request.is_json:
            json_data = request.get_json()
            current_app.logger.info(f"🔍 JSON data: {json_data}")

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
            if "photo_url" in json_data:  # Dodaj obsługę photo_url w JSON
                actor_data["photo_url"] = json_data.get("photo_url")
        else:
            # FormData request
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

            # POPRAWKA: Obsługa photo_url w update FormData
            if "photo_url" in request.form:
                photo_url_from_form = request.form.get("photo_url")
                if photo_url_from_form and photo_url_from_form.strip():
                    actor_data["photo_url"] = photo_url_from_form.strip()
                    current_app.logger.info(
                        f"🔗 Update photo_url z formularza: {photo_url_from_form}"
                    )

            # Obsługa nowego pliku (jeśli nie ma URL-a)
            elif "photo" in request.files:
                photo_file = request.files.get("photo")
                if photo_file and photo_file.filename:
                    # Upload nowego pliku
                    filename = secure_filename(photo_file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{timestamp}_{filename}"

                    upload_dir = os.path.join(current_app.static_folder, "actors")
                    os.makedirs(upload_dir, exist_ok=True)

                    file_path = os.path.join(upload_dir, filename)
                    photo_file.save(file_path)

                    actor_data["photo_url"] = filename
                    current_app.logger.info(
                        f"📁 Update - uploadowano nowy plik: {filename}"
                    )

        current_app.logger.info(
            f"📋 Dane do aktualizacji aktora {actor_id}: {actor_data}"
        )

        actor = actor_service.update_actor(actor_id, actor_data)
        if not actor:
            return jsonify({"error": "Nie znaleziono aktora"}), 404

        current_app.logger.info(
            f"✅ Zaktualizowano aktora: {actor.actor_name}, photo_url: {actor.photo_url}"
        )

        return jsonify(
            {
                "message": "Aktor został pomyślnie zaktualizowany",
                "actor": actor.serialize(),
            }
        )

    except ValueError as e:
        current_app.logger.error(f"❌ Błąd walidacji update: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"❌ Błąd aktualizacji aktora: {str(e)}")
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

    # Istniejące parametry
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # NOWE - parametry sortowania
    sort_field = request.args.get("sort_field", "release_date")
    sort_order = request.args.get("sort_order", "desc")

    # Walidacja parametrów sortowania
    valid_sort_fields = ["release_date", "title", "duration_minutes", "average_rating"]
    if sort_field not in valid_sort_fields:
        sort_field = "release_date"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    # Walidacja paginacji
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 50:
        per_page = 10

    try:
        # Wywołaj serwis z nowymi parametrami
        result = actor_service.get_actor_movies(
            actor_id, page, per_page, sort_field, sort_order
        )

        if result:
            return jsonify({"success": True, "data": result})
        else:
            return (
                jsonify({"success": False, "error": "Aktor nie został znaleziony"}),
                404,
            )

    except Exception as e:
        current_app.logger.error(f"Error in get_actor_movies: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Wystąpił błąd podczas pobierania filmów aktora",
                    "details": str(e),
                }
            ),
            500,
        )


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


# STATISTICS & DASHBOARD ENDPOINTS


@actors_bp.route("/statistics", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_actors_statistics():
    """Pobiera podstawowe statystyki aktorów"""
    if request.method == "OPTIONS":
        return

    try:
        stats = actor_service.get_actors_statistics()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting actors statistics: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania statystyk aktorów"}), 500


@actors_bp.route("/dashboard", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_actors_dashboard():
    """Pobiera kompletne dane dashboard dla aktorów"""
    if request.method == "OPTIONS":
        return

    try:
        dashboard_data = actor_service.get_dashboard_overview()
        return jsonify(dashboard_data), 200
    except Exception as e:
        current_app.logger.error(f"Error getting actors dashboard: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania dashboard aktorów"}), 500


@actors_bp.route("/analytics/popular", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_popular_actors():
    """Pobiera najpopularniejszych aktorów"""
    if request.method == "OPTIONS":
        return

    try:
        limit = request.args.get("limit", 10, type=int)
        popular_actors = actor_service.get_popular_actors(limit)
        return jsonify(popular_actors), 200
    except Exception as e:
        current_app.logger.error(f"Error getting popular actors: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania popularnych aktorów"}), 500


@actors_bp.route("/analytics/by-country", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_actors_by_country():
    """Pobiera statystyki aktorów według krajów"""
    if request.method == "OPTIONS":
        return

    try:
        country_stats = actor_service.get_actors_by_country()
        return jsonify(country_stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting actors by country: {str(e)}")
        return (
            jsonify({"error": "Błąd podczas pobierania statystyk według krajów"}),
            500,
        )


@actors_bp.route("/analytics/age-distribution", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_actors_age_distribution():
    """Pobiera rozkład wieku aktorów"""
    if request.method == "OPTIONS":
        return

    try:
        age_distribution = actor_service.get_age_distribution()
        return jsonify(age_distribution), 200
    except Exception as e:
        current_app.logger.error(f"Error getting age distribution: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania rozkładu wieku"}), 500


@actors_bp.route("/recent", methods=["GET", "OPTIONS"])
@cors_headers
@staff_required
def get_recent_actors():
    """Pobiera ostatnio dodanych aktorów"""
    if request.method == "OPTIONS":
        return

    try:
        limit = request.args.get("limit", 5, type=int)
        recent_actors = actor_service.get_recent_actors(limit)
        return jsonify(recent_actors), 200
    except Exception as e:
        current_app.logger.error(f"Error getting recent actors: {str(e)}")
        return jsonify({"error": "Błąd podczas pobierania ostatnich aktorów"}), 500
