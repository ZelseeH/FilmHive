from sqlalchemy import desc, asc, or_
from sqlalchemy.exc import SQLAlchemyError
from app.models.director import Director, Gender
from math import ceil


class DirectorRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self, page=1, per_page=10):
        try:
            total = self.session.query(Director).count()
            total_pages = ceil(total / per_page)

            directors = (
                self.session.query(Director)
                .order_by(Director.director_name)
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            pagination = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            }

            return {"directors": directors, "pagination": pagination}
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_by_id(self, director_id):
        try:
            return (
                self.session.query(Director)
                .filter(Director.director_id == director_id)
                .first()
            )
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_by_name(self, name):
        try:
            return (
                self.session.query(Director)
                .filter(Director.director_name == name)
                .first()
            )
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def add(self, director_data):
        try:
            existing_director = self.get_by_name(director_data.get("name"))
            if existing_director:
                raise ValueError(
                    f"Reżyser o nazwie '{director_data.get('name')}' już istnieje"
                )

            gender = None
            if "gender" in director_data and director_data["gender"]:
                gender_value = director_data["gender"]
                if gender_value == "M":
                    gender = Gender.M
                elif gender_value == "K":
                    gender = Gender.K

            director = Director(
                director_name=director_data.get("name"),
                birth_date=director_data.get("birth_date"),
                birth_place=director_data.get("birth_place", ""),
                biography=director_data.get("biography", ""),
                photo_url=director_data.get("photo_url"),
                gender=gender,
            )
            self.session.add(director)
            self.session.commit()
            return director
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update(self, director_id, director_data):
        try:
            director = self.get_by_id(director_id)
            if not director:
                return None

            if (
                "name" in director_data
                and director_data["name"] != director.director_name
            ):
                existing_director = self.get_by_name(director_data["name"])
                if existing_director and existing_director.director_id != director_id:
                    raise ValueError(
                        f"Reżyser o nazwie '{director_data['name']}' już istnieje"
                    )

            if "name" in director_data:
                director.director_name = director_data["name"]
            if "birth_date" in director_data:
                director.birth_date = director_data["birth_date"]
            if "birth_place" in director_data:
                director.birth_place = director_data["birth_place"]
            if "biography" in director_data:
                director.biography = director_data["biography"]
            if "photo_url" in director_data:
                director.photo_url = director_data["photo_url"]

            if "gender" in director_data:
                gender_value = director_data["gender"]
                if gender_value == "M":
                    director.gender = Gender.M
                elif gender_value == "K":
                    director.gender = Gender.K
                else:
                    director.gender = None

            self.session.commit()
            return director
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete(self, director_id):
        try:
            director = self.get_by_id(director_id)
            if not director:
                return False

            if director.movies:
                raise ValueError(
                    f"Nie można usunąć reżysera '{director.director_name}', ponieważ jest powiązany z filmami"
                )

            self.session.delete(director)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def search(self, query, page=1, per_page=10):
        try:
            search_query = f"%{query}%"
            query_obj = self.session.query(Director).filter(
                or_(
                    Director.director_name.ilike(search_query),
                    Director.birth_place.ilike(search_query),
                    Director.biography.ilike(search_query),
                )
            )

            total = query_obj.count()
            total_pages = ceil(total / per_page)

            directors = (
                query_obj.order_by(Director.director_name)
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            pagination = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            }

            return {"directors": directors, "pagination": pagination}
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_director_movies(self, director_id, page=1, per_page=10):
        try:
            director = self.get_by_id(director_id)
            if not director:
                return None

            total = len(director.movies)
            total_pages = ceil(total / per_page)

            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            movies = director.movies[start_idx:end_idx]

            pagination = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            }

            return {"movies": movies, "pagination": pagination}
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
