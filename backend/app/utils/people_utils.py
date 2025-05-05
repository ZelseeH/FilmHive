from flask import url_for
from typing import Union
from app.models.actor import Actor
from app.models.director import Director


def serialize_person(obj: Union[Actor, Director], person_type: str) -> dict:
    if person_type not in {"actor", "director"}:
        raise ValueError("person_type must be 'actor' or 'director'")

    photo_subdir = "actors" if person_type == "actor" else "directors"
    id_value = obj.actor_id if person_type == "actor" else obj.director_id
    name_value = obj.actor_name if person_type == "actor" else obj.director_name

    return {
        "id": id_value,
        "name": name_value,
        "birth_date": obj.birth_date.isoformat() if obj.birth_date else None,
        "birth_place": obj.birth_place,
        "biography": obj.biography,
        "photo_url": (
            url_for(
                "static", filename=f"{photo_subdir}/{obj.photo_url}", _external=True
            )
            if obj.photo_url
            else None
        ),
        "gender": obj.gender.value if obj.gender else None,
        "type": person_type,
    }
