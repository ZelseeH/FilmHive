from app.models.actor import Actor
from app.models.director import Director
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func, select, desc, text, union_all
from app.utils.people_utils import serialize_person, get_people_query
from flask import url_for


class PeopleRepository:
    def __init__(self, session):
        self.session = session

    def _apply_sorting(self, query, sort_by="name", sort_order="asc"):
        subquery = query.alias("people")

        if sort_by == "name":
            if sort_order.lower() == "asc":
                return select(subquery).order_by(subquery.c.name)
            else:
                return select(subquery).order_by(subquery.c.name.desc())

        elif sort_by == "birth_date":
            if sort_order.lower() == "asc":
                return select(subquery).order_by(subquery.c.birth_date)
            else:
                return select(subquery).order_by(subquery.c.birth_date.desc())

        else:
            if sort_order.lower() == "asc":
                return select(subquery).order_by(subquery.c.name)
            else:
                return select(subquery).order_by(subquery.c.name.desc())

    def get_all(
        self, page=1, per_page=10, sort_by="name", sort_order="asc", filters=None
    ):
        base_query = get_people_query(filters)
        query = self._apply_sorting(base_query, sort_by, sort_order)
        count_query = select(func.count()).select_from(base_query.alias())
        total = self.session.execute(count_query).scalar()
        final_query = query.offset((page - 1) * per_page).limit(per_page)
        result = self.session.execute(final_query)

        people = []
        for row in result:
            person_dict = {}
            for key in row._mapping.keys():
                value = row._mapping[key]
                if key == "gender" and value is not None:
                    person_dict[key] = value.value
                else:
                    person_dict[key] = value

            # Generowanie poprawnego URL dla zdjęcia
            person_type = person_dict["type"]
            if person_dict["photo_url"]:
                folder = "actors" if person_type == "actor" else "directors"
                person_dict["photo_url"] = url_for(
                    "static",
                    filename=f"{folder}/{person_dict['photo_url']}",
                    _external=True,
                )

            people.append(person_dict)

        total_pages = (total + per_page - 1) // per_page

        return {
            "people": people,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def get_by_id(self, id, person_type):
        if person_type == "actor":
            person = self.session.query(Actor).filter(Actor.actor_id == id).first()
            if person:
                return serialize_person(person, "actor")
        elif person_type == "director":
            person = (
                self.session.query(Director).filter(Director.director_id == id).first()
            )
            if person:
                return serialize_person(person, "director")
        return None

    def search(self, query, page=1, per_page=10):
        filters = {"name": query}
        return self.get_all(page, per_page, filters=filters)

    def get_person_movies(self, id, person_type, page=1, per_page=10):
        if person_type == "actor":
            actor = self.session.query(Actor).filter(Actor.actor_id == id).first()
            if not actor:
                return None

            total = len(actor.movies)
            movies = actor.movies[(page - 1) * per_page : page * per_page]

            total_pages = (total + per_page - 1) // per_page

            return {
                "movies": movies,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                },
            }

        elif person_type == "director":
            director = (
                self.session.query(Director).filter(Director.director_id == id).first()
            )
            if not director:
                return None

            total = len(director.movies)
            movies = director.movies[(page - 1) * per_page : page * per_page]

            total_pages = (total + per_page - 1) // per_page

            return {
                "movies": movies,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                },
            }

        else:
            raise ValueError("Invalid person type. Must be 'actor' or 'director'.")

    def get_unique_birthplaces(self):
        actor_query = select(
            func.split_part(Actor.birth_place, ",", -1).label("country")
        ).distinct()

        director_query = select(
            func.split_part(Director.birth_place, ",", -1).label("country")
        ).distinct()

        combined_query = union_all(actor_query, director_query)
        unique_query = (
            select(combined_query.alias().c.country)
            .distinct()
            .order_by(text("country"))
        )

        result = self.session.execute(unique_query)
        countries = [row.country.strip() for row in result if row.country]
        return countries

    def filter_people(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        return self.get_all(page, per_page, sort_by, sort_order, filters)
