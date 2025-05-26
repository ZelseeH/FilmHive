from app.models.actor import Actor
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from functools import reduce


class ActorRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self, page=1, per_page=10):
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
        return self.session.query(Actor).filter(Actor.actor_id == actor_id).first()

    def get_by_name(self, name):
        return self.session.query(Actor).filter(Actor.actor_name == name).first()

    def search(self, query, page=1, per_page=10):
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
        try:
            # Sprawdź, czy aktor o takiej nazwie już istnieje
            existing_actor = (
                self.session.query(Actor)
                .filter(Actor.actor_name == actor_data.get("name"))
                .first()
            )
            if existing_actor:
                raise ValueError(
                    f"Aktor o nazwie '{actor_data.get('name')}' już istnieje"
                )

            # Konwersja płci na enum
            gender = None
            if "gender" in actor_data and actor_data["gender"]:
                from app.models.actor import Gender

                gender_value = actor_data["gender"]
                if gender_value == "M":
                    gender = Gender.M
                elif gender_value == "K":
                    gender = Gender.K

            actor = Actor(
                actor_name=actor_data.get("name"),
                birth_date=actor_data.get("birth_date"),
                birth_place=actor_data.get("birth_place", ""),
                biography=actor_data.get("biography", ""),
                photo_url=actor_data.get("photo_url"),
                gender=gender,
            )
            self.session.add(actor)
            self.session.commit()
            return actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update(self, actor_id, actor_data):
        """Aktualizuje dane aktora o podanym ID"""
        try:
            actor = self.get_by_id(actor_id)
            if not actor:
                return None

            # Sprawdź, czy nowa nazwa nie koliduje z istniejącym aktorem
            if "name" in actor_data and actor_data["name"] != actor.actor_name:
                existing_actor = (
                    self.session.query(Actor)
                    .filter(Actor.actor_name == actor_data["name"])
                    .first()
                )
                if existing_actor and existing_actor.actor_id != actor_id:
                    raise ValueError(
                        f"Aktor o nazwie '{actor_data['name']}' już istnieje"
                    )

            # Aktualizacja pól
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

            # Aktualizacja płci
            if "gender" in actor_data:
                from app.models.actor import Gender

                gender_value = actor_data["gender"]
                if gender_value == "M":
                    actor.gender = Gender.M
                elif gender_value == "K":
                    actor.gender = Gender.K
                else:
                    actor.gender = None

            self.session.commit()
            return actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete(self, actor_id):
        """Usuwa aktora o podanym ID"""
        try:
            actor = self.get_by_id(actor_id)
            if not actor:
                return False

            # Sprawdź, czy aktor ma powiązane filmy
            if actor.movies:
                raise ValueError(
                    f"Nie można usunąć aktora '{actor.actor_name}', ponieważ jest powiązany z filmami"
                )

            self.session.delete(actor)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_actor_movies(self, actor_id, page=1, per_page=10):
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
        from sqlalchemy import or_, and_, extract, func

        if "name" in filters and filters["name"]:
            search_name = f"%{filters['name']}%"
            query = query.filter(Actor.actor_name.ilike(search_name))
        if "countries" in filters and filters["countries"]:
            countries = filters["countries"].split(",")
            country_conditions = []
            for country in countries:
                country_conditions.append(
                    Actor.birth_place.ilike(f"%{country.strip()}%")
                )
            if country_conditions:
                query = query.filter(or_(*country_conditions))

        if "years" in filters and filters["years"]:
            years = filters["years"].split(",")
            year_conditions = []
            for year in years:
                try:
                    year_conditions.append(
                        extract("year", Actor.birth_date) == int(year)
                    )
                except ValueError:
                    print(f"Invalid year: {year}")
            if year_conditions:
                query = query.filter(or_(*year_conditions))

        if "gender" in filters and filters["gender"]:
            from app.models.actor import Gender

            gender_value = filters["gender"]
            if gender_value == "M":
                query = query.filter(Actor.gender == Gender.M)
            elif gender_value == "K":
                query = query.filter(Actor.gender == Gender.K)

        if "movie_count_min" in filters and filters["movie_count_min"]:
            from app.models.movie_actor import MovieActor
            from sqlalchemy import func

            min_count = int(filters["movie_count_min"])

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

        if "popularity" in filters and filters["popularity"]:
            popularity = float(filters["popularity"])
            query = query.filter(Actor.popularity >= popularity)

        return query

    def _apply_sorting(self, query, sort_by="name", sort_order="asc"):
        from sqlalchemy import func, extract, desc

        if sort_by == "name":
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.actor_name)
            else:
                query = query.order_by(Actor.actor_name.desc())

        elif sort_by == "birth_date":
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.birth_date)
            else:
                query = query.order_by(Actor.birth_date.desc())

        elif sort_by == "movie_count":
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
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.popularity)
            else:
                query = query.order_by(Actor.popularity.desc())

        else:
            if sort_order.lower() == "asc":
                query = query.order_by(Actor.actor_name)
            else:
                query = query.order_by(Actor.actor_name.desc())

        return query

    def filter_actors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        query = self.session.query(Actor)

        query = self._apply_filters(query, filters)

        query = self._apply_sorting(query, sort_by, sort_order)

        total = query.count()
        print(f"Total actors matching filters: {total}")

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
        query = (
            self.session.query(
                func.split_part(Actor.birth_place, ",", -1).label("country")
            )
            .distinct()
            .order_by("country")
        )

        countries = [row.country.strip() for row in query.all() if row.country]
        return countries

    def search(self, query, page=1, per_page=10):
        search_query = f"%{query}%"
        total = (
            self.session.query(Actor)
            .filter(Actor.actor_name.ilike(search_query))
            .count()
        )

        actors = (
            self.session.query(Actor)
            .filter(Actor.actor_name.ilike(search_query))
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
        # STATISTICS & DASHBOARD METHODS

    def get_actors_statistics(self):
        """Pobiera podstawowe statystyki aktorów"""
        try:
            from sqlalchemy import func, extract
            from datetime import datetime, timedelta

            # Podstawowe statystyki
            total_actors = self.session.query(Actor).count()

            # Aktorzy z ostatnich 30 dni
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_actors = (
                self.session.query(Actor)
                .filter(Actor.created_at >= thirty_days_ago)
                .count()
                if hasattr(Actor, "created_at")
                else 0
            )

            # Aktorzy według płci
            male_count = self.session.query(Actor).filter(Actor.gender == "M").count()
            female_count = self.session.query(Actor).filter(Actor.gender == "K").count()
            unknown_gender = total_actors - male_count - female_count

            # Aktorzy ze zdjęciami
            with_photos = (
                self.session.query(Actor).filter(Actor.photo_url.isnot(None)).count()
            )
            without_photos = total_actors - with_photos

            # Średni wiek (jeśli mamy daty urodzenia)
            actors_with_birth_date = (
                self.session.query(Actor).filter(Actor.birth_date.isnot(None)).all()
            )

            average_age = 0
            if actors_with_birth_date:
                current_year = datetime.utcnow().year
                ages = []
                for actor in actors_with_birth_date:
                    if actor.birth_date:
                        age = current_year - actor.birth_date.year
                        if 0 <= age <= 120:  # Realistyczne granice wieku
                            ages.append(age)
                average_age = sum(ages) / len(ages) if ages else 0

            return {
                "total_actors": total_actors,
                "recent_actors_30_days": recent_actors,
                "gender_distribution": {
                    "male": male_count,
                    "female": female_count,
                    "unknown": unknown_gender,
                },
                "photo_statistics": {
                    "with_photos": with_photos,
                    "without_photos": without_photos,
                    "photo_percentage": (
                        round((with_photos / total_actors * 100), 2)
                        if total_actors > 0
                        else 0
                    ),
                },
                "average_age": round(average_age, 1) if average_age > 0 else None,
            }

        except Exception as e:
            print(f"Błąd podczas pobierania statystyk aktorów: {e}")
            raise

    def get_actors_by_country(self):
        """Pobiera statystyki aktorów według krajów"""
        try:
            from sqlalchemy import func

            country_stats = (
                self.session.query(
                    Actor.birth_place, func.count(Actor.actor_id).label("count")
                )
                .filter(Actor.birth_place.isnot(None))
                .group_by(Actor.birth_place)
                .order_by(func.count(Actor.actor_id).desc())
                .limit(10)
                .all()
            )

            return [
                {"country": country, "count": count} for country, count in country_stats
            ]

        except Exception as e:
            print(f"Błąd podczas pobierania statystyk według krajów: {e}")
            raise

    def get_age_distribution(self):
        """Pobiera rozkład wieku aktorów"""
        try:
            from datetime import datetime

            actors_with_birth_date = (
                self.session.query(Actor).filter(Actor.birth_date.isnot(None)).all()
            )

            age_ranges = {
                "0-20": 0,
                "21-30": 0,
                "31-40": 0,
                "41-50": 0,
                "51-60": 0,
                "61-70": 0,
                "71+": 0,
            }

            current_year = datetime.utcnow().year

            for actor in actors_with_birth_date:
                if actor.birth_date:
                    age = current_year - actor.birth_date.year

                    if 0 <= age <= 20:
                        age_ranges["0-20"] += 1
                    elif 21 <= age <= 30:
                        age_ranges["21-30"] += 1
                    elif 31 <= age <= 40:
                        age_ranges["31-40"] += 1
                    elif 41 <= age <= 50:
                        age_ranges["41-50"] += 1
                    elif 51 <= age <= 60:
                        age_ranges["51-60"] += 1
                    elif 61 <= age <= 70:
                        age_ranges["61-70"] += 1
                    elif age > 70:
                        age_ranges["71+"] += 1

            return [
                {"age_range": age_range, "count": count}
                for age_range, count in age_ranges.items()
            ]

        except Exception as e:
            print(f"Błąd podczas pobierania rozkładu wieku: {e}")
            raise

    def get_popular_actors(self, limit=10):
        """Pobiera najpopularniejszych aktorów (według liczby filmów)"""
        try:
            from sqlalchemy import func

            # Zakładając, że masz tabelę movie_actors łączącą aktorów z filmami
            popular_actors = (
                self.session.query(Actor, func.count().label("movie_count"))
                .outerjoin(Actor.movies)  # Zakładając relationship 'movies'
                .group_by(Actor.actor_id)
                .order_by(func.count().desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": actor.actor_id,
                    "name": actor.actor_name,  # POPRAWKA: actor_name zamiast name
                    "photo_url": actor.photo_url,
                    "movie_count": movie_count,
                    "birth_place": actor.birth_place,
                }
                for actor, movie_count in popular_actors
            ]

        except Exception as e:
            print(f"Błąd podczas pobierania popularnych aktorów: {e}")
            # Fallback - zwróć po prostu pierwszych N aktorów
            actors = self.session.query(Actor).limit(limit).all()
            return [
                {
                    "id": actor.actor_id,
                    "name": actor.actor_name,  # POPRAWKA: actor_name zamiast name
                    "photo_url": actor.photo_url,
                    "movie_count": 0,
                    "birth_place": actor.birth_place,
                }
                for actor in actors
            ]

    def get_recent_actors(self, limit=5):
        """Pobiera ostatnio dodanych aktorów"""
        try:
            # Jeśli masz pole created_at
            if hasattr(Actor, "created_at"):
                recent_actors = (
                    self.session.query(Actor)
                    .order_by(Actor.created_at.desc())
                    .limit(limit)
                    .all()
                )
            else:
                # Fallback - sortuj po ID (zakładając że wyższe ID = nowsze)
                recent_actors = (
                    self.session.query(Actor)
                    .order_by(Actor.actor_id.desc())
                    .limit(limit)
                    .all()
                )

            return [
                {
                    "id": actor.actor_id,
                    "name": actor.actor_name,  # POPRAWKA: actor_name zamiast name
                    "photo_url": actor.photo_url,
                    "birth_place": actor.birth_place,
                    "birth_date": (
                        actor.birth_date.isoformat() if actor.birth_date else None
                    ),
                }
                for actor in recent_actors
            ]

        except Exception as e:
            print(f"Błąd podczas pobierania ostatnich aktorów: {e}")
            raise

    def get_dashboard_data(self):
        """Pobiera wszystkie dane potrzebne do dashboard"""
        try:
            return {
                "statistics": self.get_actors_statistics(),
                "country_distribution": self.get_actors_by_country(),
                "age_distribution": self.get_age_distribution(),
                "popular_actors": self.get_popular_actors(5),
                "recent_actors": self.get_recent_actors(5),
            }

        except Exception as e:
            print(f"Błąd podczas pobierania danych dashboard: {e}")
            raise
