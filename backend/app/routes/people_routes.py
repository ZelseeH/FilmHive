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
    per_page = request.args.get("per_page", 10, type=int)
    sort_by = request.args.get("sort_by", "name")
    sort_order = request.args.get("sort_order", "asc")

    filters = {}
    if "type" in request.args:
        filters["type"] = request.args.get("type")
    if "name" in request.args:
        filters["name"] = request.args.get("name")
    if "countries" in request.args:
        filters["countries"] = request.args.get("countries")
    if "years" in request.args:
        filters["years"] = request.args.get("years")
    if "gender" in request.args:
        filters["gender"] = request.args.get("gender")

    result = people_service.get_all_people(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        filters=filters,
    )
    return jsonify(result)


@people_bp.route("/<string:type>/<int:id>", methods=["GET", "OPTIONS"])
@cors_headers
def get_person(type, id):
    if request.method == "OPTIONS":
        return

    person = people_service.get_person_by_id(id, type)
    if person:
        return jsonify(person)
    return jsonify({"error": "Person not found"}), 404


@people_bp.route("/search", methods=["GET", "OPTIONS"])
@cors_headers
def search_people():
    if request.method == "OPTIONS":
        return

    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = people_service.search_people(query, page, per_page)
    return jsonify(result)


@people_bp.route("/<string:type>/<int:id>/movies", methods=["GET", "OPTIONS"])
@cors_headers
def get_person_movies(type, id):
    if request.method == "OPTIONS":
        return

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = people_service.get_person_movies(id, type, page, per_page)
    if result:
        return jsonify(result)
    return jsonify({"error": "Person not found"}), 404


@people_bp.route("/filter", methods=["GET", "OPTIONS"])
@cors_headers
def filter_people():
    if request.method == "OPTIONS":
        return

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)

        filters = {}
        if "type" in request.args:
            filters["type"] = request.args.get("type")
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
                {
                    "error": "Wystąpił błąd podczas filtrowania osób",
                    "details": str(e),
                }
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


# Funkcja do rejestracji blueprintu
def register_people_blueprint(app):
    app.register_blueprint(people_bp)
