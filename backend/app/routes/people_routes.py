from flask import Blueprint, jsonify
from app.models.actor import Actor
from app.models.director import Director
from app.utils.people_utils import serialize_person
from app import db

people_bp = Blueprint("people", __name__)


@people_bp.route("/api/people")
def get_people():
    actors = db.session.query(Actor).all()  # Poprawione
    directors = db.session.query(Director).all()  # Poprawione

    people = [serialize_person(actor, "actor") for actor in actors] + [
        serialize_person(director, "director") for director in directors
    ]

    return jsonify(people)
