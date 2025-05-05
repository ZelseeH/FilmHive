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

    def get_person_by_id(self, id, person_type):
        return self.people_repository.get_by_id(id, person_type)

    def search_people(self, query, page=1, per_page=10):
        result = self.people_repository.search(query, page, per_page)
        return {"people": result["people"], "pagination": result["pagination"]}

    def get_person_movies(self, id, person_type, page=1, per_page=10):
        result = self.people_repository.get_person_movies(
            id, person_type, page, per_page
        )
        if not result:
            return None

        movies = result["movies"]
        pagination = result["pagination"]

        serialized_movies = []
        for movie in movies:
            # Dodajemy parametr include_actors_roles=True dla aktorów
            if person_type == "actor":
                movie_data = movie.serialize(
                    include_actors=True,
                    include_actors_roles=True,
                    include_directors=True,
                )
            else:
                movie_data = movie.serialize(
                    include_actors=True, include_directors=True
                )

            # Dodajemy informację o roli dla aktora
            if person_type == "actor" and "actors" in movie_data:
                movie_data["actor_role"] = next(
                    (
                        actor["role"]
                        for actor in movie_data["actors"]
                        if actor["id"] == id
                    ),
                    None,
                )
                # Usuwamy tablicę aktorów, aby zmniejszyć rozmiar odpowiedzi
                del movie_data["actors"]

            serialized_movies.append(movie_data)

        return {"movies": serialized_movies, "pagination": pagination}

    def filter_people(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        try:
            result = self.people_repository.filter_people(
                filters,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            return {
                "people": result["people"],
                "pagination": result["pagination"],
                "sort_by": sort_by,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in filter_people: {str(e)}")
            raise Exception(f"Error filtering people: {str(e)}")

    def get_unique_birthplaces(self):
        return self.people_repository.get_unique_birthplaces()

    # Metody kompatybilności wstecznej dla aktorów
    def get_all_actors(self, page=1, per_page=10):
        filters = {"type": "actor"}
        result = self.get_all_people(page, per_page, filters=filters)
        return {"actors": result["people"], "pagination": result["pagination"]}

    def get_actor_by_id(self, actor_id):
        return self.get_person_by_id(actor_id, "actor")

    def search_actors(self, query, page=1, per_page=10):
        result = self.search_people(query, page, per_page)
        # Filtrujemy tylko aktorów z wyników
        actors = [
            person for person in result["people"] if person.get("type") == "actor"
        ]
        return {"actors": actors, "pagination": result["pagination"]}

    def get_actor_movies(self, actor_id, page=1, per_page=10):
        return self.get_person_movies(actor_id, "actor", page, per_page)

    def filter_actors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        actor_filters = filters.copy()
        actor_filters["type"] = "actor"

        try:
            result = self.filter_people(
                actor_filters,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
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

    # Metody kompatybilności wstecznej dla reżyserów
    def get_all_directors(self, page=1, per_page=10):
        filters = {"type": "director"}
        result = self.get_all_people(page, per_page, filters=filters)
        return {"directors": result["people"], "pagination": result["pagination"]}

    def get_director_by_id(self, director_id):
        return self.get_person_by_id(director_id, "director")

    def search_directors(self, query, page=1, per_page=10):
        result = self.search_people(query, page, per_page)
        # Filtrujemy tylko reżyserów z wyników
        directors = [
            person for person in result["people"] if person.get("type") == "director"
        ]
        return {"directors": directors, "pagination": result["pagination"]}

    def get_director_movies(self, director_id, page=1, per_page=10):
        return self.get_person_movies(director_id, "director", page, per_page)

    def filter_directors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        director_filters = filters.copy()
        director_filters["type"] = "director"

        try:
            result = self.filter_people(
                director_filters,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
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
