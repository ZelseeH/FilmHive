from flask import Blueprint, jsonify, request, current_app, make_response
from app.services.people_service import PeopleService

people_bp = Blueprint("people", __name__, url_prefix="/api/people")
people_service = PeopleService()


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


@people_bp.route("/", methods=["GET", "OPTIONS"])
@cors_headers
def get_all_people():
    if request.method == "OPTIONS":
        return
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10)
    if per_page == "all":
        per_page = None
    else:
        per_page = int(per_page)
    sort_by = request.args.get("sort_by", "name")
    sort_order = request.args.get("sort_order", "asc")

    filters = {}
    for key in ["type", "name", "countries", "years", "gender"]:
        if key in request.args:
            filters[key] = request.args.get(key)

    result = people_service.get_all_people(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        filters=filters,
    )
    return jsonify(result)


@people_bp.route("/<string:type>/<string:identifier>", methods=["GET", "OPTIONS"])
@cors_headers
def get_person_universal(type, identifier):
    if request.method == "OPTIONS":
        return
    try:
        if identifier.isdigit():
            current_app.logger.info(f"Fetching {type} by ID: {identifier}")
            person = people_service.get_person_by_id(int(identifier), type)
            if person:
                return jsonify(person)

        current_app.logger.info(f"Fetching {type} by slug: {identifier}")
        name = identifier.replace("-", " ").title()
        person = people_service.get_person_by_slug(name, type)
        if person:
            return jsonify(person)

        # Try searching without .title()
        person = people_service.get_person_by_slug(identifier.replace("-", " "), type)
        if person:
            return jsonify(person)

        current_app.logger.warning(
            f"{type.title()} not found for identifier: {identifier}"
        )
        return jsonify({"error": f"{type.title()} nie został znaleziony"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching {type} {identifier}: {str(e)}")
        return jsonify({"error": "Wystąpił błąd podczas pobierania danych"}), 500


@people_bp.route("/search", methods=["GET", "OPTIONS"])
@cors_headers
def search_people():
    if request.method == "OPTIONS":
        return
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10)
    if per_page == "all":
        per_page = None
    else:
        per_page = int(per_page)
    result = people_service.search_people(query, page, per_page)
    return jsonify(result)


@people_bp.route(
    "/<string:type>/<string:identifier>/movies", methods=["GET", "OPTIONS"]
)
@cors_headers
def get_person_movies(type, identifier):
    if request.method == "OPTIONS":
        return
    try:
        person_id = None
        if identifier.isdigit():
            person_id = int(identifier)
        else:
            name = identifier.replace("-", " ").title()
            person = people_service.get_person_by_slug(name, type)
            if person and "id" in person:
                person_id = person["id"]

        if not person_id:
            return jsonify({"error": f"{type.title()} nie został znaleziony"}), 404

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", "10")
        if per_page == "all":
            per_page = None
        else:
            per_page = int(per_page)

        sort_field = request.args.get("sort_field", "release_date")
        sort_order = request.args.get("sort_order", "desc")

        valid_sort_fields = [
            "release_date",
            "title",
            "duration_minutes",
            "average_rating",
        ]
        if sort_field not in valid_sort_fields:
            sort_field = "release_date"
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        if page < 1:
            page = 1
        if per_page and (per_page < 1 or per_page > 100):
            per_page = 10

        result = people_service.get_person_movies(
            person_id, type, page, per_page, sort_field, sort_order
        )
        if result:
            return jsonify({"success": True, "data": result})
        else:
            return (
                jsonify(
                    {"success": False, "error": f"{type.title()} nie został znaleziony"}
                ),
                404,
            )
    except Exception as e:
        current_app.logger.error(
            f"Error fetching movies for {type} {identifier}: {str(e)}"
        )
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Wystąpił błąd podczas pobierania filmów",
                    "details": str(e),
                }
            ),
            500,
        )


@people_bp.route("/filter", methods=["GET", "OPTIONS"])
@cors_headers
def filter_people():
    if request.method == "OPTIONS":
        return
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10)
        if per_page == "all":
            per_page = None
        else:
            per_page = int(per_page)
        per_page = min(per_page or 1000000, 100)

        filters = {}
        for key in ["type", "name", "countries", "years", "gender"]:
            if key in request.args:
                filters[key] = request.args.get(key)

        sort_by = request.args.get("sort_by", "name")
        sort_order = request.args.get("sort_order", "asc")

        valid_sort_fields = ["name", "birth_date"]
        valid_sort_orders = ["asc", "desc"]

        if sort_by not in valid_sort_fields:
            sort_by = "name"
        if sort_order.lower() not in valid_sort_orders:
            sort_order = "asc"

        result = people_service.filter_people(
            filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in filter_people route: {str(e)}")
        return (
            jsonify(
                {"error": "Wystąpił błąd podczas filtrowania osób", "details": str(e)}
            ),
            500,
        )


@people_bp.route("/birthplaces", methods=["GET", "OPTIONS"])
@cors_headers
def get_birthplaces():
    if request.method == "OPTIONS":
        return
    birthplaces = people_service.get_unique_birthplaces()
    return jsonify({"birthplaces": birthplaces})


@people_bp.route("/birthdays/today", methods=["GET"])
@cors_headers
def get_today_birthdays():
    try:
        people = people_service.get_people_with_birthday_today()
        return jsonify({"birthdays_today": people}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching today's birthdays: {e}")
        return jsonify({"error": "Błąd podczas pobierania urodzin"}), 500


def register_people_blueprint(app):
    app.register_blueprint(people_bp)
