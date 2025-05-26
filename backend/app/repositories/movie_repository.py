from app.models.movie import Movie
from app.models.genre import Genre
from app.models.rating import Rating
from sqlalchemy import func, or_, extract, desc
from sqlalchemy.orm import joinedload, selectinload


class MovieRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return (
            self.session.query(Movie)
            .options(joinedload(Movie.genres), selectinload(Movie.ratings))
            .all()
        )

    def get_paginated(self, page=1, per_page=10, genre_id=None, user_id=None):
        movies, total = Movie.get_with_ratings(
            self.session,
            page=page,
            per_page=per_page,
            genre_id=genre_id,
            user_id=user_id,
        )
        total_pages = (total + per_page - 1) // per_page
        return {
            "movies": movies,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    def get_top_rated(self, limit=10, user_id=None):
        query = (
            self.session.query(
                Movie,
                func.avg(Rating.rating).label("avg_rating"),
                func.count(Rating.rating_id).label("rating_count"),
            )
            .outerjoin(Rating, Movie.movie_id == Rating.movie_id)
            .group_by(Movie.movie_id)
            .order_by(func.count(Rating.rating_id).desc())  # Sortowanie po liczbie ocen
            .options(joinedload(Movie.genres))
            .limit(limit)
        )

        movies_with_ratings = query.all()

        user_ratings = {}
        if user_id:
            user_ratings_query = (
                self.session.query(Rating.movie_id, Rating.rating)
                .filter(Rating.user_id == user_id)
                .filter(
                    Rating.movie_id.in_(
                        [movie.movie_id for movie, _, _ in movies_with_ratings]
                    )
                )
            )
            user_ratings = {movie_id: rating for movie_id, rating in user_ratings_query}

        result = []
        for movie, avg_rating, rating_count in movies_with_ratings:
            movie._average_rating = (
                float(avg_rating) if avg_rating is not None else None
            )
            movie._rating_count = rating_count or 0
            movie._user_rating = user_ratings.get(movie.movie_id)
            result.append(movie)

        return result

    def get_by_id(self, movie_id, user_id=None):
        movie = (
            self.session.query(Movie)
            .options(
                joinedload(Movie.genres),
                selectinload(Movie.ratings),
                selectinload(Movie.actors),
                selectinload(Movie.directors),
            )
            .get(movie_id)
        )

        if movie and user_id:
            user_rating = (
                self.session.query(Rating.rating)
                .filter(Rating.user_id == user_id, Rating.movie_id == movie_id)
                .scalar()
            )
            movie._user_rating = user_rating

        return movie

    def add(self, movie):
        self.session.add(movie)
        self.session.commit()
        return movie

    def delete(self, movie_id):
        movie = self.get_by_id(movie_id)
        if movie:
            self.session.delete(movie)
            self.session.commit()
            return True
        return False

    def get_filter_options(self):
        if hasattr(self, "_filter_options_cache"):
            return self._filter_options_cache

        genres = self.session.query(Genre).order_by(Genre.genre_name).all()
        countries = (
            self.session.query(Movie.country).distinct().order_by(Movie.country).all()
        )
        countries = [c[0] for c in countries if c[0]]
        result = {
            "genres": [{"id": g.genre_id, "name": g.genre_name} for g in genres],
            "countries": countries,
        }
        self._filter_options_cache = result
        return result

    def _apply_filters(self, query, filters):
        if filters.get("title"):
            query = query.filter(Movie.title.ilike(f"%{filters['title']}%"))

        if filters.get("countries"):
            query = query.filter(Movie.country.in_(filters["countries"].split(",")))

        if filters.get("years"):
            years = [int(y) for y in filters["years"].split(",") if y]
            if years:
                query = query.filter(
                    or_(*[extract("year", Movie.release_date) == y for y in years])
                )

        if filters.get("genres"):
            genre_ids = [int(g) for g in filters["genres"].split(",") if g.isdigit()]
            if genre_ids:
                query = query.join(Movie.genres).filter(Genre.genre_id.in_(genre_ids))

        if filters.get("rating_count_min") or filters.get("average_rating"):
            ratings_subquery = (
                self.session.query(
                    Rating.movie_id,
                    func.count(Rating.rating_id).label("count"),
                    func.avg(Rating.rating).label("avg_rating"),
                )
                .group_by(Rating.movie_id)
                .subquery()
            )
            query = query.outerjoin(
                ratings_subquery, Movie.movie_id == ratings_subquery.c.movie_id
            )

            if filters.get("rating_count_min"):
                query = query.filter(
                    ratings_subquery.c.count >= int(filters["rating_count_min"])
                )

            if filters.get("average_rating"):
                query = query.filter(
                    ratings_subquery.c.avg_rating >= float(filters["average_rating"])
                )

        return query

    def _apply_sorting(self, query, sort_by="title", sort_order="asc"):
        if sort_by in ["average_rating", "rating_count"]:
            ratings_subquery = (
                self.session.query(
                    Rating.movie_id,
                    func.avg(Rating.rating).label("avg_rating"),
                    func.count(Rating.rating_id).label("count"),
                )
                .group_by(Rating.movie_id)
                .subquery()
            )
            query = query.outerjoin(
                ratings_subquery, Movie.movie_id == ratings_subquery.c.movie_id
            )

            if sort_by == "average_rating":
                order = (
                    func.coalesce(ratings_subquery.c.avg_rating, 0).asc()
                    if sort_order.lower() == "asc"
                    else func.coalesce(ratings_subquery.c.avg_rating, 0).desc()
                )
                query = query.order_by(order)
            else:
                order = (
                    func.coalesce(ratings_subquery.c.count, 0).asc()
                    if sort_order.lower() == "asc"
                    else func.coalesce(ratings_subquery.c.count, 0).desc()
                )
                query = query.order_by(order)
        elif sort_by == "year":
            order = (
                extract("year", Movie.release_date).asc()
                if sort_order.lower() == "asc"
                else extract("year", Movie.release_date).desc()
            )
            query = query.order_by(order)
        else:
            order = (
                Movie.title.asc() if sort_order.lower() == "asc" else Movie.title.desc()
            )
            query = query.order_by(order)

        return query

    def filter_movies(
        self,
        filters,
        page=1,
        per_page=10,
        sort_by="title",
        sort_order="asc",
        user_id=None,
    ):
        query = self.session.query(Movie)
        query = query.options(joinedload(Movie.genres), selectinload(Movie.ratings))
        query = self._apply_filters(query, filters)
        query = self._apply_sorting(query, sort_by, sort_order)

        total = query.count()
        movies = query.offset((page - 1) * per_page).limit(per_page).all()

        if user_id:
            movie_ids = [movie.movie_id for movie in movies]
            user_ratings = (
                self.session.query(Rating.movie_id, Rating.rating)
                .filter(Rating.user_id == user_id)
                .filter(Rating.movie_id.in_(movie_ids))
                .all()
            )

            ratings_map = {movie_id: rating for movie_id, rating in user_ratings}
            for movie in movies:
                movie._user_rating = ratings_map.get(movie.movie_id)
                print(f"Movie: {movie.title}, user_rating: {movie._user_rating}")

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

    def search(self, query, page=1, per_page=10, user_id=None):
        filters = {"title": query}
        return self.filter_movies(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by="title",
            sort_order="asc",
            user_id=user_id,
        )

    def get_all_with_title_filter(self, title_filter=None, page=1, per_page=10):
        try:
            query = self.session.query(Movie).options(
                joinedload(Movie.genres),
                selectinload(Movie.actors),
                selectinload(Movie.directors),
            )

            if title_filter and title_filter.strip():
                query = query.filter(Movie.title.ilike(f"%{title_filter}%"))

            query = query.order_by(Movie.title.asc())

            total = query.count()
            movies = query.offset((page - 1) * per_page).limit(per_page).all()

            total_pages = (total + per_page - 1) // per_page

            return {
                "movies": movies,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            }
        except Exception as e:
            print(f"Error in get_all_with_title_filter: {str(e)}")
            return {
                "movies": [],
                "pagination": {
                    "page": 1,
                    "per_page": per_page,
                    "total": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False,
                },
            }

    def update(self, movie_id, data):
        try:
            movie = self.session.query(Movie).filter(Movie.movie_id == movie_id).first()
            if not movie:
                return None

            # Aktualizuj pola jeśli są podane
            if "title" in data:
                movie.title = data["title"]
            if "description" in data:
                movie.description = data["description"]
            if "release_date" in data:
                movie.release_date = data["release_date"]
            if "duration_minutes" in data:
                movie.duration_minutes = data["duration_minutes"]
            if "country" in data:
                movie.country = data["country"]
            if "original_language" in data:
                movie.original_language = data["original_language"]
            if "trailer_url" in data:
                movie.trailer_url = data["trailer_url"]
            if "poster_url" in data:
                movie.poster_url = data["poster_url"]

            self.session.commit()
            return movie
        except Exception as e:
            self.session.rollback()
            raise e

    def update_poster(self, movie_id, poster_url):
        try:
            movie = self.session.query(Movie).filter(Movie.movie_id == movie_id).first()
            if not movie:
                return None

            movie.poster_url = poster_url
            self.session.commit()
            return movie
        except Exception as e:
            self.session.rollback()
            raise e

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki filmów"""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta

            # Podstawowe liczby
            total_movies = self.session.query(Movie).count()

            # Filmy z ostatnich 30 dni (jeśli masz pole created_at)
            if hasattr(Movie, "created_at"):
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                recent_movies = (
                    self.session.query(Movie)
                    .filter(Movie.created_at >= thirty_days_ago)
                    .count()
                )
            else:
                recent_movies = 0

            # POPRAWKA - Średnia ocena z tabeli ratings
            try:
                from app.models.rating import Rating

                avg_rating = self.session.query(func.avg(Rating.rating)).scalar()
            except:
                # Fallback - jeśli nie ma tabeli ratings
                avg_rating = 0

            # Filmy z plakatami
            with_posters = (
                self.session.query(Movie).filter(Movie.poster_url.isnot(None)).count()
            )
            without_posters = total_movies - with_posters

            # POPRAWKA - Sprawdź czy duration_minutes to kolumna czy property
            try:
                longest_movie = self.session.query(
                    func.max(Movie.duration_minutes)
                ).scalar()
                shortest_movie = self.session.query(
                    func.min(Movie.duration_minutes)
                ).scalar()
                avg_duration = self.session.query(
                    func.avg(Movie.duration_minutes)
                ).scalar()
            except:
                # Fallback jeśli duration_minutes to property
                longest_movie = 0
                shortest_movie = 0
                avg_duration = 0

            return {
                "total_movies": total_movies,
                "recent_movies_30_days": recent_movies,
                "average_rating": round(avg_rating, 2) if avg_rating else 0,
                "poster_statistics": {
                    "with_posters": with_posters,
                    "without_posters": without_posters,
                    "poster_percentage": (
                        round((with_posters / total_movies * 100), 2)
                        if total_movies > 0
                        else 0
                    ),
                },
                "duration_statistics": {
                    "average_duration": round(avg_duration, 1) if avg_duration else 0,
                    "longest_movie": longest_movie or 0,
                    "shortest_movie": shortest_movie or 0,
                },
            }

        except Exception as e:
            print(f"Błąd podczas pobierania podstawowych statystyk: {e}")
            # Zwróć podstawowe dane w przypadku błędu
            total_movies = self.session.query(Movie).count()
            return {
                "total_movies": total_movies,
                "recent_movies_30_days": 0,
                "average_rating": 0,
                "poster_statistics": {
                    "with_posters": 0,
                    "without_posters": total_movies,
                    "poster_percentage": 0,
                },
                "duration_statistics": {
                    "average_duration": 0,
                    "longest_movie": 0,
                    "shortest_movie": 0,
                },
            }

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla filmów"""
        try:
            from sqlalchemy import func, extract
            from datetime import datetime

            # Podstawowe statystyki
            basic_stats = self.get_basic_statistics()

            # POPRAWKA - Top 10 najlepiej ocenianych filmów
            # Nie możemy użyć Movie.average_rating w SQL, bo to property
            # Musimy obliczyć średnią bezpośrednio z tabeli ratings
            try:
                from app.models.rating import Rating

                # Subquery do obliczenia średniej oceny
                avg_rating_subq = (
                    self.session.query(
                        Rating.movie_id, func.avg(Rating.rating).label("avg_rating")
                    )
                    .group_by(Rating.movie_id)
                    .subquery()
                )

                # Join z subquery i sortowanie
                top_rated_movies_query = (
                    self.session.query(Movie, avg_rating_subq.c.avg_rating)
                    .join(avg_rating_subq, Movie.movie_id == avg_rating_subq.c.movie_id)
                    .order_by(avg_rating_subq.c.avg_rating.desc())
                    .limit(10)
                    .all()
                )

                top_rated_movies = [
                    {
                        "id": movie.movie_id,
                        "title": movie.title,
                        "rating": float(avg_rating) if avg_rating else 0,
                        "poster_url": (
                            f"http://localhost:5000/static/posters/{movie.poster_url}"
                            if movie.poster_url
                            else None
                        ),  # POPRAWKA URL
                    }
                    for movie, avg_rating in top_rated_movies_query
                ]
            except Exception as e:
                print(f"Błąd w top_rated_movies: {e}")
                # Fallback - zwróć po prostu pierwsze 10 filmów
                movies = self.session.query(Movie).limit(10).all()
                top_rated_movies = [
                    {
                        "id": movie.movie_id,
                        "title": movie.title,
                        "rating": 0,
                        "poster_url": (
                            f"http://localhost:5000/static/posters/{movie.poster_url}"
                            if movie.poster_url
                            else None
                        ),  # POPRAWKA URL
                    }
                    for movie in movies
                ]

            # Filmy według lat (ostatnie 10 lat)
            current_year = datetime.utcnow().year
            movies_by_year = []
            for year in range(current_year - 9, current_year + 1):
                count = (
                    self.session.query(Movie)
                    .filter(extract("year", Movie.release_date) == year)
                    .count()
                )
                movies_by_year.append({"year": year, "count": count})

            # Top 5 gatunków (jeśli masz relationship z gatunkami)
            try:
                from app.models.genre import Genre

                top_genres = (
                    self.session.query(
                        Genre.genre_name,  # POPRAWKA: genre_name zamiast name
                        func.count(Movie.movie_id).label("movie_count"),
                    )
                    .join(Movie.genres)  # Zakładając many-to-many relationship
                    .group_by(Genre.genre_id, Genre.genre_name)  # POPRAWKA: genre_name
                    .order_by(func.count(Movie.movie_id).desc())
                    .limit(5)
                    .all()
                )
                genre_distribution = [
                    {"genre": name, "movie_count": count} for name, count in top_genres
                ]
            except Exception as e:
                print(f"Błąd w genre_distribution: {e}")
                genre_distribution = []

            # POPRAWKA - Rozkład ocen
            # Nie możemy użyć Movie.average_rating w SQL
            try:
                from app.models.rating import Rating

                rating_distribution = []
                for rating in [1, 2, 3, 4, 5]:
                    count = (
                        self.session.query(Rating)
                        .filter(
                            Rating.rating >= rating,
                            Rating.rating < rating + 1,
                        )
                        .count()
                    )
                    rating_distribution.append(
                        {"rating_range": f"{rating}-{rating+1}", "count": count}
                    )
            except Exception as e:
                print(f"Błąd w rating_distribution: {e}")
                rating_distribution = []

            # Ostatnio dodane filmy
            recent_movies = (
                self.session.query(Movie)
                .order_by(Movie.movie_id.desc())  # Lub Movie.created_at jeśli masz
                .limit(5)
                .all()
            )

            return {
                "statistics": basic_stats,
                "top_rated_movies": top_rated_movies,
                "movies_by_year": movies_by_year,
                "genre_distribution": genre_distribution,
                "rating_distribution": rating_distribution,
                "recent_movies": [
                    {
                        "id": movie.movie_id,
                        "title": movie.title,
                        "release_date": (
                            movie.release_date.isoformat()
                            if movie.release_date
                            else None
                        ),
                        "poster_url": (
                            f"http://localhost:5000/static/posters/{movie.poster_url}"
                            if movie.poster_url
                            else None
                        ),  # POPRAWKA URL
                    }
                    for movie in recent_movies
                ],
            }

        except Exception as e:
            print(f"Błąd podczas pobierania danych dashboard: {e}")
            raise
