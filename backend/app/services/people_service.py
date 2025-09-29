from app.repositories.people_repository import PeopleRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import os


class PeopleService:
    def __init__(self):
        self.people_repository = PeopleRepository(db.session)

    def get_all_people(
        self, page=1, per_page=10, sort_by="name", sort_order="asc", filters=None
    ):
        try:
            result = self.people_repository.get_all(
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
                filters=filters,
            )
            return {
                "people": result["people"],
                "pagination": result["pagination"],
                "sort_by": sort_by,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in get_all_people: {str(e)}")
            raise

    def get_person_by_id(self, id, person_type):
        try:
            return self.people_repository.get_by_id(id, person_type)
        except Exception as e:
            current_app.logger.error(f"Error in get_person_by_id: {str(e)}")
            raise

    def get_person_by_slug(self, name, person_type):
        try:
            if person_type == "actor":
                from app.models.actor import Actor

                person = Actor.query.filter(Actor.actor_name.ilike(name)).first()
                if not person:
                    person = Actor.query.filter(
                        Actor.actor_name.ilike(f"%{name}%")
                    ).first()
                return person.serialize() if person else None

            elif person_type == "director":
                from app.models.director import Director

                person = Director.query.filter(
                    Director.director_name.ilike(name)
                ).first()
                if not person:
                    person = Director.query.filter(
                        Director.director_name.ilike(f"%{name}%")
                    ).first()
                return person.serialize() if person else None

            else:
                current_app.logger.warning(f"Unknown person_type: {person_type}")
                return None
        except Exception as e:
            current_app.logger.error(
                f"Error in get_person_by_slug for {person_type} '{name}': {str(e)}"
            )
            return None

    def search_people(self, query, page=1, per_page=10):
        try:
            result = self.people_repository.search(query, page, per_page)
            return {"people": result["people"], "pagination": result["pagination"]}
        except Exception as e:
            current_app.logger.error(f"Error in search_people: {str(e)}")
            raise

    def get_person_movies(
        self,
        id,
        person_type,
        page=1,
        per_page=10,
        sort_field="release_date",
        sort_order="desc",
    ):
        try:
            result = self.people_repository.get_person_movies(
                id, person_type, page, per_page, sort_field, sort_order
            )
            if not result:
                return None

            movies = []
            for movie in result["movies"]:
                movie_data = movie.serialize(
                    include_actors=True,
                    include_actors_roles=(person_type == "actor"),
                    include_directors=True,
                )
                if person_type == "actor" and "actors" in movie_data:
                    movie_data["actor_role"] = next(
                        (
                            actor["role"]
                            for actor in movie_data["actors"]
                            if actor["id"] == id
                        ),
                        None,
                    )
                    del movie_data["actors"]
                movies.append(movie_data)

            return {
                "movies": movies,
                "pagination": result["pagination"],
                "sort_field": sort_field,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in get_person_movies: {str(e)}")
            raise

    def filter_people(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        try:
            result = self.people_repository.filter_people(
                filters, page, per_page, sort_by, sort_order
            )
            return {
                "people": result["people"],
                "pagination": result["pagination"],
                "sort_by": sort_by,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in filter_people: {str(e)}")
            raise

    def get_unique_birthplaces(self):
        try:
            return self.people_repository.get_unique_birthplaces()
        except Exception as e:
            current_app.logger.error(f"Error in get_unique_birthplaces: {str(e)}")
            raise

    def get_all_actors(self, page=1, per_page=10):
        filters = {"type": "actor"}
        result = self.get_all_people(page, per_page, filters=filters)
        return {"actors": result["people"], "pagination": result["pagination"]}

    def get_actor_by_id(self, actor_id):
        return self.get_person_by_id(actor_id, "actor")

    def search_actors(self, query, page=1, per_page=10):
        result = self.search_people(query, page, per_page)
        actors = [p for p in result["people"] if p.get("type") == "actor"]
        return {"actors": actors, "pagination": result["pagination"]}

    def get_actor_movies(
        self,
        actor_id,
        page=1,
        per_page=10,
        sort_field="release_date",
        sort_order="desc",
    ):
        return self.get_person_movies(
            actor_id, "actor", page, per_page, sort_field, sort_order
        )

    def filter_actors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        actor_filters = filters.copy()
        actor_filters["type"] = "actor"
        try:
            result = self.filter_people(
                actor_filters, page, per_page, sort_by, sort_order
            )
            return {
                "actors": result["people"],
                "pagination": result["pagination"],
                "sort_by": sort_by,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in filter_actors: {str(e)}")
            raise Exception(f"Błąd podczas filtrowania aktorów: {str(e)}")

    def get_all_directors(self, page=1, per_page=10):
        filters = {"type": "director"}
        result = self.get_all_people(page, per_page, filters=filters)
        return {"directors": result["people"], "pagination": result["pagination"]}

    def get_director_by_id(self, director_id):
        return self.get_person_by_id(director_id, "director")

    def search_directors(self, query, page=1, per_page=10):
        result = self.search_people(query, page, per_page)
        directors = [p for p in result["people"] if p.get("type") == "director"]
        return {"directors": directors, "pagination": result["pagination"]}

    def get_director_movies(
        self,
        director_id,
        page=1,
        per_page=10,
        sort_field="release_date",
        sort_order="desc",
    ):
        return self.get_person_movies(
            director_id, "director", page, per_page, sort_field, sort_order
        )

    def filter_directors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        director_filters = filters.copy()
        director_filters["type"] = "director"
        try:
            result = self.filter_people(
                director_filters, page, per_page, sort_by, sort_order
            )
            return {
                "directors": result["people"],
                "pagination": result["pagination"],
                "sort_by": sort_by,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in filter_directors: {str(e)}")
            raise Exception(f"Błąd podczas filtrowania reżyserów: {str(e)}")

    def get_people_with_birthday_today(self):
        try:
            return self.people_repository.get_people_with_birthday_today()
        except Exception as e:
            current_app.logger.error(
                f"Error fetching people with birthday today: {str(e)}"
            )
            return []
