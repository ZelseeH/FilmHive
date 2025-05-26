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

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki reżyserów"""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta

            # Podstawowe liczby
            total_directors = self.session.query(Director).count()

            # Reżyserzy według płci
            male_count = (
                self.session.query(Director).filter(Director.gender == "M").count()
            )
            female_count = (
                self.session.query(Director).filter(Director.gender == "K").count()
            )
            unknown_gender = total_directors - male_count - female_count

            # Reżyserzy ze zdjęciami
            with_photos = (
                self.session.query(Director)
                .filter(Director.photo_url.isnot(None))
                .count()
            )
            without_photos = total_directors - with_photos

            # Średni wiek (jeśli mamy daty urodzenia)
            directors_with_birth_date = (
                self.session.query(Director)
                .filter(Director.birth_date.isnot(None))
                .all()
            )

            average_age = 0
            if directors_with_birth_date:
                current_year = datetime.utcnow().year
                ages = []
                for director in directors_with_birth_date:
                    if director.birth_date:
                        age = current_year - director.birth_date.year
                        if 0 <= age <= 120:
                            ages.append(age)
                average_age = sum(ages) / len(ages) if ages else 0

            return {
                "total_directors": total_directors,
                "gender_distribution": {
                    "male": male_count,
                    "female": female_count,
                    "unknown": unknown_gender,
                },
                "photo_statistics": {
                    "with_photos": with_photos,
                    "without_photos": without_photos,
                    "photo_percentage": (
                        round((with_photos / total_directors * 100), 2)
                        if total_directors > 0
                        else 0
                    ),
                },
                "average_age": round(average_age, 1) if average_age > 0 else None,
            }

        except Exception as e:
            print(f"Błąd podczas pobierania podstawowych statystyk: {e}")
            raise

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla reżyserów"""
        try:
            from sqlalchemy import func

            # Podstawowe statystyki
            basic_stats = self.get_basic_statistics()

            # Top 5 krajów z największą liczbą reżyserów
            top_countries = (
                self.session.query(
                    Director.birth_place,
                    func.count(Director.director_id).label("count"),
                )
                .filter(Director.birth_place.isnot(None))
                .group_by(Director.birth_place)
                .order_by(func.count(Director.director_id).desc())
                .limit(5)
                .all()
            )

            # Rozkład wieku
            directors_with_birth_date = (
                self.session.query(Director)
                .filter(Director.birth_date.isnot(None))
                .all()
            )

            age_ranges = {
                "20-30": 0,
                "31-40": 0,
                "41-50": 0,
                "51-60": 0,
                "61-70": 0,
                "71+": 0,
            }

            from datetime import datetime

            current_year = datetime.utcnow().year

            for director in directors_with_birth_date:
                if director.birth_date:
                    age = current_year - director.birth_date.year
                    if 20 <= age <= 30:
                        age_ranges["20-30"] += 1
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

            # Ostatnio dodani reżyserzy (top 5)
            recent_directors = (
                self.session.query(Director)
                .order_by(Director.director_id.desc())
                .limit(5)
                .all()
            )

            return {
                "statistics": basic_stats,
                "top_countries": [
                    {"country": country, "count": count}
                    for country, count in top_countries
                ],
                "age_distribution": [
                    {"age_range": age_range, "count": count}
                    for age_range, count in age_ranges.items()
                ],
                "recent_directors": [
                    {
                        "id": director.director_id,
                        "name": director.director_name,  # POPRAWKA: director_name zamiast name
                        "birth_place": director.birth_place,
                        "photo_url": director.photo_url,
                    }
                    for director in recent_directors
                ],
            }

        except Exception as e:
            print(f"Błąd podczas pobierania danych dashboard: {e}")
            raise
