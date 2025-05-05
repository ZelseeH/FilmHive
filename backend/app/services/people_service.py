from app.repositories.people_repository import PeopleRepository
from app.utils.people_utils import serialize_person
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app


class PeopleService:
    def __init__(self):
        self.people_repository = PeopleRepository(db.session)

    def get_people(self, person_type, page=1, per_page=10):
        try:
            result = self.people_repository.get_all(person_type, page, per_page)
            return {
                "data": [
                    serialize_person(person, person_type) for person in result["people"]
                ],
                "pagination": result["pagination"],
            }
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting people: {str(e)}")
            raise Exception("Failed to fetch people")

    def get_person(self, person_type, person_id):
        try:
            person = self.people_repository.get_by_id(person_type, person_id)
            return serialize_person(person, person_type) if person else None
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting person: {str(e)}")
            raise Exception("Failed to fetch person")

    def search_people(self, person_type, query, page=1, per_page=10):
        try:
            result = self.people_repository.search(person_type, query, page, per_page)
            return {
                "data": [
                    serialize_person(person, person_type) for person in result["people"]
                ],
                "pagination": result["pagination"],
            }
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error searching people: {str(e)}")
            raise Exception("Search failed")

    def filter_people(
        self,
        person_type,
        filters,
        page=1,
        per_page=10,
        sort_by="name",
        sort_order="asc",
    ):
        try:
            result = self.people_repository.filter_people(
                person_type=person_type,
                filters=filters,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            return {
                "data": [
                    serialize_person(person, person_type) for person in result["people"]
                ],
                "pagination": result["pagination"],
                "sort": {"by": sort_by, "order": sort_order},
            }
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error filtering people: {str(e)}")
            raise Exception("Filtering failed")

    def get_person_movies(self, person_type, person_id, page=1, per_page=10):
        try:
            result = self.people_repository.get_person_movies(
                person_type, person_id, page, per_page
            )
            if not result:
                return None

            return {
                "movies": [movie.serialize() for movie in result["movies"]],
                "pagination": result["pagination"],
            }
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting person movies: {str(e)}")
            raise Exception("Failed to fetch movies")

    def get_unique_birthplaces(self, person_type):
        try:
            return self.people_repository.get_unique_birthplaces(person_type)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting birthplaces: {str(e)}")
            raise Exception("Failed to fetch birthplaces")
