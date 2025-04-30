from app.models.movie import Movie
from app.models.genre import Genre


class MovieRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Movie).all()

    def get_paginated(self, page=1, per_page=10, genre_id=None):
        query = self.session.query(Movie)

        if genre_id:
            query = query.join(Movie.genres).filter(Genre.genre_id == genre_id)

        offset = (page - 1) * per_page

        total = query.count()

        movies = query.order_by(Movie.title).offset(offset).limit(per_page).all()

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

<<<<<<< Updated upstream
    def get_by_id(self, movie_id):
        return self.session.get(Movie, movie_id)
=======
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

        for movie in result:
            print(f"\nFilm: {movie.title} (ID: {movie.movie_id})")
            print("Genres:")
            for genre in movie.genres:
                print(f"  Type: {type(genre)}")
                print(f"  genre_id: {getattr(genre, 'genre_id', None)}")
                print(f"  genre_name: {getattr(genre, 'genre_name', None)}")

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
>>>>>>> Stashed changes

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
        from app.models.genre import Genre

        genres = self.session.query(Genre).order_by(Genre.genre_name).all()

        countries = (
            self.session.query(Movie.country).distinct().order_by(Movie.country).all()
        )
        countries = [country[0] for country in countries if country[0]]

        return {
            "genres": [{"id": g.genre_id, "name": g.genre_name} for g in genres],
            "countries": countries,
        }

    def _apply_filters(self, query, filters):
        from sqlalchemy import func, and_, or_, extract
        from app.models.rating import Rating

        if "title" in filters and filters["title"]:
            search_title = f"%{filters['title']}%"
            query = query.filter(Movie.title.ilike(search_title))

        if "countries" in filters and filters["countries"]:
            countries = filters["countries"].split(",")
            query = query.filter(Movie.country.in_(countries))

        if "years" in filters and filters["years"]:
            years = filters["years"].split(",")
            year_conditions = []
            for year in years:
                year_conditions.append(extract("year", Movie.release_date) == int(year))
            if year_conditions:
                query = query.filter(or_(*year_conditions))

        if "genres" in filters and filters["genres"]:
            from app.models.genre import Genre

            print(f"Filtering by genres: {filters['genres']}")
            genres = filters["genres"].split(",")
            print(f"Parsed genre IDs: {genres}")

            genre_ids = []
            for genre_id in genres:
                try:
                    genre_ids.append(int(genre_id))
                except ValueError:
                    print(f"Invalid genre ID: {genre_id}")

            print(f"Converted genre IDs: {genre_ids}")

            if genre_ids:
                existing_genres = (
                    self.session.query(Genre.genre_id)
                    .filter(Genre.genre_id.in_(genre_ids))
                    .all()
                )
                existing_genre_ids = [g[0] for g in existing_genres]
                print(f"Existing genre IDs in database: {existing_genre_ids}")

                query = query.join(Movie.genres).filter(Genre.genre_id.in_(genre_ids))

                print(f"SQL Query: {query}")

        if "rating_count_min" in filters and filters["rating_count_min"]:
            min_count = int(filters["rating_count_min"])
            print(f"Filtering by minimum rating count: {min_count}")

            rating_count_subquery = (
                self.session.query(
                    Rating.movie_id, func.count(Rating.rating_id).label("count")
                )
                .group_by(Rating.movie_id)
                .subquery()
            )

            query = query.join(
                rating_count_subquery,
                Movie.movie_id == rating_count_subquery.c.movie_id,
            )

            query = query.filter(rating_count_subquery.c.count >= min_count)

        if "average_rating" in filters and filters["average_rating"]:
            avg_rating = float(filters["average_rating"])
            print(f"Filtering by minimum average rating: {avg_rating}")

            avg_rating_subquery = (
                self.session.query(
                    Rating.movie_id, func.avg(Rating.rating).label("avg_rating")
                )
                .group_by(Rating.movie_id)
                .subquery()
            )
            query = query.join(
                avg_rating_subquery,
                Movie.movie_id == avg_rating_subquery.c.movie_id,
            )

            query = query.filter(avg_rating_subquery.c.avg_rating >= avg_rating)

        return query

    def _apply_sorting(self, query, sort_by="title", sort_order="asc"):
        from sqlalchemy import func, extract
        from app.models.rating import Rating

        print(f"Sorting by: {sort_by}, order: {sort_order}")

        if sort_by == "average_rating":
            avg_rating_subquery = (
                self.session.query(
                    Rating.movie_id, func.avg(Rating.rating).label("avg_rating")
                )
                .group_by(Rating.movie_id)
                .subquery()
            )
            query = query.outerjoin(
                avg_rating_subquery, Movie.movie_id == avg_rating_subquery.c.movie_id
            )
            if sort_order.lower() == "asc":
                query = query.order_by(
                    func.coalesce(avg_rating_subquery.c.avg_rating, 0)
                )
            else:
                query = query.order_by(
                    func.coalesce(avg_rating_subquery.c.avg_rating, 0).desc()
                )

        elif sort_by == "rating_count":
            rating_count_subquery = (
                self.session.query(
                    Rating.movie_id, func.count(Rating.rating_id).label("count")
                )
                .group_by(Rating.movie_id)
                .subquery()
            )
            query = query.outerjoin(
                rating_count_subquery,
                Movie.movie_id == rating_count_subquery.c.movie_id,
            )
            if sort_order.lower() == "asc":
                query = query.order_by(func.coalesce(rating_count_subquery.c.count, 0))
            else:
                query = query.order_by(
                    func.coalesce(rating_count_subquery.c.count, 0).desc()
                )

        elif sort_by == "year":
            if sort_order.lower() == "asc":
                query = query.order_by(extract("year", Movie.release_date))
            else:
                query = query.order_by(extract("year", Movie.release_date).desc())

        else:
            if sort_order.lower() == "asc":
                query = query.order_by(Movie.title)
            else:
                query = query.order_by(Movie.title.desc())

        return query

    def filter_movies(
        self, filters, page=1, per_page=10, sort_by="title", sort_order="asc"
    ):
        from sqlalchemy import func, and_, or_, extract
        from app.models.rating import Rating

        query = self.session.query(Movie)

        query = self._apply_filters(query, filters)

        query = self._apply_sorting(query, sort_by, sort_order)

        total = query.count()
        print(f"Total movies matching filters: {total}")

        movies = query.offset((page - 1) * per_page).limit(per_page).all()

        print(f"Returned movies: {len(movies)}")
        if movies:
            print(f"First movie: {movies[0].title}")

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
