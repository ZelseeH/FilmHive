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
