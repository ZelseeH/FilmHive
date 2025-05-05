from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func, and_, extract
from app.models.actor import Actor
from app.models.director import Director
from functools import reduce


class PeopleRepository:
    MODEL_MAP = {
        "actor": {
            "model": Actor,
            "id_column": Actor.actor_id,
            "name_column": Actor.actor_name,
            "birth_date": Actor.birth_date,
            "birth_place": Actor.birth_place,
            "biography": Actor.biography,
            "gender": Actor.gender,
            "movies_relationship": "movies",
            "photo_url": Actor.photo_url,
        },
        "director": {
            "model": Director,
            "id_column": Director.director_id,
            "name_column": Director.director_name,
            "birth_date": Director.birth_date,
            "birth_place": Director.birth_place,
            "biography": Director.biography,
            "gender": Director.gender,
            "movies_relationship": "movies",
            "photo_url": Director.photo_url,
        },
    }

    def __init__(self, session):
        self.session = session

    def _get_model_info(self, person_type):
        return self.MODEL_MAP.get(person_type)

    def get_all(self, person_type, page=1, per_page=10):
        model_info = self._get_model_info(person_type)
        query = self.session.query(model_info["model"])

        total = query.count()
        people = (
            query.order_by(model_info["name_column"])
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "people": people,
            "pagination": self._build_pagination(page, per_page, total),
        }

    def get_by_id(self, person_type, person_id):
        model_info = self._get_model_info(person_type)
        return (
            self.session.query(model_info["model"])
            .filter(model_info["id_column"] == person_id)
            .first()
        )

    def search(self, person_type, query, page=1, per_page=10):
        model_info = self._get_model_info(person_type)
        search_term = f"%{query}%"

        total = (
            self.session.query(model_info["model"])
            .filter(
                or_(
                    model_info["name_column"].ilike(search_term),
                    model_info["biography"].ilike(search_term),
                )
            )
            .count()
        )

        people = (
            self.session.query(model_info["model"])
            .filter(
                or_(
                    model_info["name_column"].ilike(search_term),
                    model_info["biography"].ilike(search_term),
                )
            )
            .order_by(model_info["name_column"])
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "people": people,
            "pagination": self._build_pagination(page, per_page, total),
        }

    def _apply_filters(self, query, filters, model_info):
        if "name" in filters and filters["name"]:
            search_name = f"%{filters['name']}%"
            query = query.filter(model_info["name_column"].ilike(search_name))

        if "countries" in filters and filters["countries"]:
            countries = [c.strip() for c in filters["countries"].split(",")]
            country_conditions = [
                model_info["birth_place"].ilike(f"%{country}%") for country in countries
            ]
            if country_conditions:
                query = query.filter(or_(*country_conditions))

        if "years" in filters and filters["years"]:
            years = [y.strip() for y in filters["years"].split(",")]
            year_conditions = [
                extract("year", model_info["birth_date"]) == int(year)
                for year in years
                if year.isdigit()
            ]
            if year_conditions:
                query = query.filter(or_(*year_conditions))

        if "gender" in filters and filters["gender"]:
            query = query.filter(model_info["gender"] == filters["gender"])

        return query

    def _apply_sorting(self, query, model_info, sort_by="name", sort_order="asc"):
        sort_column = model_info["name_column"]

        if sort_by == "birth_date":
            sort_column = model_info["birth_date"]
        elif sort_by == "movie_count":
            from app.models.movie_actor import MovieActor

            sort_column = func.count(MovieActor.movie_id)

        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        return query

    def filter_people(
        self,
        person_type,
        filters,
        page=1,
        per_page=10,
        sort_by="name",
        sort_order="asc",
    ):
        model_info = self._get_model_info(person_type)
        query = self.session.query(model_info["model"])

        query = self._apply_filters(query, filters, model_info)
        query = self._apply_sorting(query, model_info, sort_by, sort_order)

        total = query.count()
        people = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "people": people,
            "pagination": self._build_pagination(page, per_page, total),
        }

    def get_person_movies(self, person_type, person_id, page=1, per_page=10):
        model_info = self._get_model_info(person_type)
        person = self.get_by_id(person_type, person_id)

        if not person:
            return None

        movies = getattr(person, model_info["movies_relationship"])
        total = len(movies)
        paginated_movies = movies[(page - 1) * per_page : page * per_page]

        return {
            "movies": paginated_movies,
            "pagination": self._build_pagination(page, per_page, total),
        }

    def get_unique_birthplaces(self, person_type):
        model_info = self._get_model_info(person_type)
        return (
            self.session.query(func.distinct(model_info["birth_place"]))
            .order_by(model_info["birth_place"])
            .scalars()
            .all()
        )

    def _build_pagination(self, page, per_page, total):
        return {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        }
