from flask import url_for
from sqlalchemy import union_all, select, extract, or_
from sqlalchemy.orm import aliased
from app.models.actor import Actor
from app.models.director import Director
from app.extensions import db
from urllib.parse import urlparse


def is_full_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https")


def serialize_person(person, person_type):
    folder = "actors" if person_type == "actor" else "directors"
    id_field = "actor_id" if person_type == "actor" else "director_id"
    name_field = "actor_name" if person_type == "actor" else "director_name"

    photo_url_value = getattr(person, "photo_url", None)
    if photo_url_value and is_full_url(photo_url_value):
        photo_url_final = photo_url_value
    elif photo_url_value:
        photo_url_final = url_for(
            "static", filename=f"{folder}/{photo_url_value}", _external=True
        )
    else:
        photo_url_final = None

    result = {
        "id": getattr(person, id_field),
        "name": getattr(person, name_field),
        "birth_date": person.birth_date.isoformat() if person.birth_date else None,
        "birth_place": person.birth_place,
        "biography": person.biography,
        "photo_url": photo_url_final,
        "gender": person.gender.value if person.gender else None,
        "type": person_type,
    }

    return result


def get_people_query(filters=None):
    actor_alias = aliased(Actor, name="actor")
    director_alias = aliased(Director, name="director")

    actors_query = select(
        actor_alias.actor_id.label("id"),
        actor_alias.actor_name.label("name"),
        actor_alias.birth_date,
        actor_alias.birth_place,
        actor_alias.biography,
        actor_alias.photo_url,
        actor_alias.gender,
        db.literal_column("'actor'").label("type"),
    )

    directors_query = select(
        director_alias.director_id.label("id"),
        director_alias.director_name.label("name"),
        director_alias.birth_date,
        director_alias.birth_place,
        director_alias.biography,
        director_alias.photo_url,
        director_alias.gender,
        db.literal_column("'director'").label("type"),
    )

    if filters:
        if "name" in filters:
            name_filter = f"%{filters['name']}%"
            actors_query = actors_query.where(actor_alias.actor_name.ilike(name_filter))
            directors_query = directors_query.where(
                director_alias.director_name.ilike(name_filter)
            )

        if "gender" in filters:
            gender_filter = filters["gender"]
            actors_query = actors_query.where(actor_alias.gender == gender_filter)
            directors_query = directors_query.where(
                director_alias.gender == gender_filter
            )

        if "countries" in filters:
            countries = filters["countries"].split(",")
            actor_country_conditions = [
                actor_alias.birth_place.ilike(f"%{c.strip()}%") for c in countries
            ]
            director_country_conditions = [
                director_alias.birth_place.ilike(f"%{c.strip()}%") for c in countries
            ]
            if actor_country_conditions:
                actors_query = actors_query.where(or_(*actor_country_conditions))
            if director_country_conditions:
                directors_query = directors_query.where(
                    or_(*director_country_conditions)
                )

        if "years" in filters:
            years = filters["years"].split(",")
            actor_year_conditions = [
                extract("year", actor_alias.birth_date) == int(y.strip()) for y in years
            ]
            director_year_conditions = [
                extract("year", director_alias.birth_date) == int(y.strip())
                for y in years
            ]
            if actor_year_conditions:
                actors_query = actors_query.where(or_(*actor_year_conditions))
            if director_year_conditions:
                directors_query = directors_query.where(or_(*director_year_conditions))

        if "type" in filters:
            if filters["type"] == "actor":
                return actors_query
            elif filters["type"] == "director":
                return directors_query

    union_query = union_all(actors_query, directors_query)
    return union_query
