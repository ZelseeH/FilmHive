from app.models.actor import Actor
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func  # Dodaj import func tutaj
from functools import reduce


class ActorRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self, page=1, per_page=10):
        """Pobiera wszystkich aktorów z paginacją."""
        total = self.session.query(Actor).count()
        actors = (
            self.session.query(Actor)
            .order_by(Actor.actor_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "actors": actors,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def get_by_id(self, actor_id):
        """Pobiera aktora na podstawie ID."""
        return self.session.query(Actor).filter(Actor.actor_id == actor_id).first()

    def search(self, query, page=1, per_page=10):
        """Wyszukuje aktorów na podstawie zapytania."""
        search_query = f"%{query}%"
        total = (
            self.session.query(Actor)
            .filter(
                or_(
                    Actor.actor_name.ilike(search_query),
                    Actor.biography.ilike(search_query),
                )
            )
            .count()
        )

        actors = (
            self.session.query(Actor)
            .filter(
                or_(
                    Actor.actor_name.ilike(search_query),
                    Actor.biography.ilike(search_query),
                )
            )
            .order_by(Actor.actor_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "actors": actors,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def add(self, actor_data):
        """Dodaje nowego aktora."""
        try:
            actor = Actor(
                actor_name=actor_data.get("name"),
                birth_date=actor_data.get("birth_date"),
                birth_place=actor_data.get("birth_place"),
                biography=actor_data.get("biography"),
                photo_url=actor_data.get("photo_url"),
            )
            self.session.add(actor)
            self.session.commit()
            return actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update(self, actor_id, actor_data):
        """Aktualizuje dane aktora."""
        try:
            actor = self.get_by_id(actor_id)
            if not actor:
                return None

            if "name" in actor_data:
                actor.actor_name = actor_data["name"]
            if "birth_date" in actor_data:
                actor.birth_date = actor_data["birth_date"]
            if "birth_place" in actor_data:
                actor.birth_place = actor_data["birth_place"]
            if "biography" in actor_data:
                actor.biography = actor_data["biography"]
            if "photo_url" in actor_data:
                actor.photo_url = actor_data["photo_url"]

            self.session.commit()
            return actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete(self, actor_id):
        """Usuwa aktora."""
        try:
            actor = self.get_by_id(actor_id)
            if not actor:
                return False

            self.session.delete(actor)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_actor_movies(self, actor_id, page=1, per_page=10):
        """Pobiera filmy, w których wystąpił aktor."""
        actor = self.get_by_id(actor_id)
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

    def _apply_filters(self, query, filters):
        """Aplikuje filtry do zapytania."""
        from sqlalchemy import or_, and_, extract, func

        # Filtrowanie po nazwie aktora
        if "name" in filters and filters["name"]:
            search_name = f"%{filters['name']}%"
            query = query.filter(Actor.actor_name.ilike(search_name))

        # Filtrowanie po krajach (miejsce urodzenia)
        if "countries" in filters and filters["countries"]:
            countries = filters["countries"].split(",")
            country_conditions = []
            for country in countries:
                country_conditions.append(
                    Actor.birth_place.ilike(f"%{country.strip()}%")
                )
            if country_conditions:
                query = query.filter(or_(*country_conditions))

        # Filtrowanie po latach urodzenia
        if "years" in filters and filters["years"]:
            years = filters["years"].split(",")
            year_conditions = []
            for year in years:
                try:
                    # Używamy extract zamiast between dla większej precyzji
                    year_conditions.append(
                        extract("year", Actor.birth_date) == int(year)
                    )
                except ValueError:
                    print(f"Invalid year: {year}")
            if year_conditions:
                query = query.filter(or_(*year_conditions))

        # Filtrowanie po płci
        if "gender" in filters and filters["gender"]:
            from app.models.actor import Gender

            gender_value = filters["gender"]
            if gender_value == "M":
                query = query.filter(Actor.gender == Gender.M)
            elif gender_value == "K":
                query = query.filter(Actor.gender == Gender.K)

        # Filtrowanie po liczbie filmów
        if "movie_count_min" in filters and filters["movie_count_min"]:
            from app.models.movie_actor import MovieActor
            from sqlalchemy import func

            min_count = int(filters["movie_count_min"])

            # Tworzymy podzapytanie do zliczania filmów
            movie_count_subquery = (
                self.session.query(
                    MovieActor.actor_id, func.count(MovieActor.movie_id).label("count")
                )
                .group_by(MovieActor.actor_id)
                .subquery()
            )

            query = query.join(
                movie_count_subquery,
                Actor.actor_id == movie_count_subquery.c.actor_id,
            )

            query = query.filter(movie_count_subquery.c.count >= min_count)

        # Filtrowanie po popularności (możesz dostosować to do swojego modelu)
        if "popularity" in filters and filters["popularity"]:
            popularity = float(filters["popularity"])
            query = query.filter(Actor.popularity >= popularity)

        return query

    def _apply_sorting(self, query, sort_by="name", sort_order="asc"):
        """Aplikuje sortowanie do zapytania."""
        from sqlalchemy import func, extract, desc

        if sort_by == "name":
            # Sortowanie po nazwie aktora
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.actor_name)
            else:
                query = query.order_by(Actor.actor_name.desc())

        elif sort_by == "birth_date":
            # Sortowanie po dacie urodzenia
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.birth_date)
            else:
                query = query.order_by(Actor.birth_date.desc())

        elif sort_by == "movie_count":
            # Sortowanie po liczbie filmów
            from app.models.movie_actor import MovieActor

            movie_count_subquery = (
                self.session.query(
                    MovieActor.actor_id, func.count(MovieActor.movie_id).label("count")
                )
                .group_by(MovieActor.actor_id)
                .subquery()
            )

            query = query.outerjoin(
                movie_count_subquery, Actor.actor_id == movie_count_subquery.c.actor_id
            )

            if sort_order.lower() == "asc":
                query = query.order_by(func.coalesce(movie_count_subquery.c.count, 0))
            else:
                query = query.order_by(
                    func.coalesce(movie_count_subquery.c.count, 0).desc()
                )

        elif sort_by == "popularity":
            # Sortowanie po popularności (dostosuj do swojego modelu)
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.popularity)
            else:
                query = query.order_by(Actor.popularity.desc())

        else:
            # Domyślne sortowanie po nazwie
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.actor_name)
            else:
                query = query.order_by(Actor.actor_name.desc())

        return query

    def filter_actors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        """Filtruje aktorów na podstawie różnych kryteriów i sortuje wyniki."""
        # Budowanie podstawowego zapytania
        query = self.session.query(Actor)

        # Zastosowanie filtrów
        query = self._apply_filters(query, filters)

        # Zastosowanie sortowania
        query = self._apply_sorting(query, sort_by, sort_order)

        # Obliczanie całkowitej liczby wyników
        total = query.count()
        print(f"Total actors matching filters: {total}")

        # Dodanie paginacji
        actors = query.offset((page - 1) * per_page).limit(per_page).all()

        print(f"Returned actors: {len(actors)}")
        if actors:
            print(f"First actor: {actors[0].actor_name}")

        total_pages = (total + per_page - 1) // per_page

        return {
            "actors": actors,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def get_unique_birthplaces(self):
        """Pobiera unikalne miejsca urodzenia aktorów."""
        # Wyciągnij kraj z pola birth_place (zakładając format "miasto, kraj")
        query = (
            self.session.query(
                func.split_part(Actor.birth_place, ",", -1).label("country")
            )
            .distinct()
            .order_by("country")
        )

        countries = [row.country.strip() for row in query.all() if row.country]
        return countries
