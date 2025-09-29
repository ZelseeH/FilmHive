from app.models.actor import Actor
from app.models.director import Director
from app.models.movie import Movie
from app.models.movie_actor import MovieActor
from app.models.movie_director import MovieDirector
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func, select, desc, asc, text, union_all
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

    def _process_photo_url(self, person_dict, person_type):
        """Pomocnicza metoda do obsługi URL zdjęć"""
        if person_dict.get("photo_url"):
            photo_url_lower = person_dict["photo_url"].lower()
            if not (
                "tmdb" in photo_url_lower
                or photo_url_lower.startswith("http://")
                or photo_url_lower.startswith("https://")
            ):
                folder = "actors" if person_type == "actor" else "directors"
                photo_url_final = url_for(
                    "static",
                    filename=f"{folder}/{person_dict['photo_url']}",
                    _external=True,
                )
                person_dict["photo_url"] = photo_url_final
        return person_dict

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

            person_type = person_dict["type"]
            person_dict = self._process_photo_url(person_dict, person_type)
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
                person_dict = serialize_person(person, "actor")
                return self._process_photo_url(person_dict, "actor")
        elif person_type == "director":
            person = (
                self.session.query(Director).filter(Director.director_id == id).first()
            )
            if person:
                person_dict = serialize_person(person, "director")
                return self._process_photo_url(person_dict, "director")
        return None

    def get_by_name(self, name, person_type):
        """Wyszukuje osobę po nazwie (slug)"""
        try:
            if person_type == "actor":
                person = (
                    self.session.query(Actor)
                    .filter(Actor.actor_name.ilike(name))
                    .first()
                )
                if not person:
                    person = (
                        self.session.query(Actor)
                        .filter(Actor.actor_name.ilike(f"%{name}%"))
                        .first()
                    )
                if person:
                    person_dict = serialize_person(person, "actor")
                    return self._process_photo_url(person_dict, "actor")

            elif person_type == "director":
                person = (
                    self.session.query(Director)
                    .filter(Director.director_name.ilike(name))
                    .first()
                )
                if not person:
                    person = (
                        self.session.query(Director)
                        .filter(Director.director_name.ilike(f"%{name}%"))
                        .first()
                    )
                if person:
                    person_dict = serialize_person(person, "director")
                    return self._process_photo_url(person_dict, "director")

            return None

        except SQLAlchemyError as e:
            print(f"Database error in get_by_name: {e}")
            return None

    def search(self, query, page=1, per_page=10):
        filters = {"name": query}
        return self.get_all(page, per_page, filters=filters)

    def get_person_movies(
        self,
        id,
        person_type,
        page=1,
        per_page=None,
        sort_field="release_date",
        sort_order="desc",
    ):
        try:
            if person_type == "actor":
                query = (
                    self.session.query(Movie)
                    .join(MovieActor, Movie.movie_id == MovieActor.movie_id)
                    .filter(MovieActor.actor_id == id)
                )
            elif person_type == "director":
                query = (
                    self.session.query(Movie)
                    .join(MovieDirector, Movie.movie_id == MovieDirector.movie_id)
                    .filter(MovieDirector.director_id == id)
                )
            else:
                raise ValueError("Invalid person type. Must be 'actor' or 'director'.")

            valid_sort_fields = [
                "release_date",
                "title",
                "duration_minutes",
                "average_rating",
            ]
            if sort_field not in valid_sort_fields:
                sort_field = "release_date"

            if sort_order not in ["asc", "desc"]:
                sort_order = "desc"

            sort_column = getattr(Movie, sort_field)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            total = query.count()

            if per_page is None:
                movies = query.all()
                total_pages = 1
                current_page = 1
            else:
                movies = query.offset((page - 1) * per_page).limit(per_page).all()
                total_pages = (total + per_page - 1) // per_page
                current_page = page

            return {
                "movies": movies,
                "pagination": {
                    "page": current_page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                },
            }
        except Exception as e:
            print(f"Błąd podczas pobierania filmów osoby: {e}")
            return None

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

    def get_people_with_birthday_today(self):
        actor_query = select(
            func.cast(text("'actor'"), type_=Actor.actor_name.type).label("type"),
            Actor.actor_id.label("id"),
            Actor.actor_name.label("name"),
            Actor.birth_date,
            Actor.photo_url,  # dodane pole zdjęcia aktora
            func.extract("year", func.age(Actor.birth_date)).label("age"),
        ).where(
            func.extract("month", Actor.birth_date)
            == func.extract("month", func.current_date()),
            func.extract("day", Actor.birth_date)
            == func.extract("day", func.current_date()),
        )

        director_query = select(
            func.cast(text("'director'"), type_=Director.director_name.type).label(
                "type"
            ),
            Director.director_id.label("id"),
            Director.director_name.label("name"),
            Director.birth_date,
            Director.photo_url,  # dodane pole zdjęcia reżysera
            func.extract("year", func.age(Director.birth_date)).label("age"),
        ).where(
            func.extract("month", Director.birth_date)
            == func.extract("month", func.current_date()),
            func.extract("day", Director.birth_date)
            == func.extract("day", func.current_date()),
        )

        combined_query = union_all(actor_query, director_query)

        result = self.session.execute(combined_query)
        people = [
            {
                "type": row.type,
                "id": row.id,
                "name": row.name,
                "birth_date": row.birth_date,
                "photo_url": row.photo_url,
                "age": int(row.age),
            }
            for row in result
        ]
        return people
