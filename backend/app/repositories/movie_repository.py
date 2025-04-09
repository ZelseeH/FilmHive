from app.models.movie import Movie
from app.models.genre import Genre


class MovieRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Movie).all()

    def get_paginated(self, page=1, per_page=10, genre_id=None):
        """Pobiera filmy z paginacją, opcjonalnie filtrując po gatunku."""
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

    def get_by_id(self, movie_id):
        return self.session.get(Movie, movie_id)

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
        """Pobiera dostępne opcje filtrów dla filmów."""
        from app.models.genre import Genre

        # Pobierz wszystkie gatunki
        genres = self.session.query(Genre).order_by(Genre.genre_name).all()

        # Pobierz wszystkie kraje
        countries = (
            self.session.query(Movie.country).distinct().order_by(Movie.country).all()
        )
        countries = [country[0] for country in countries if country[0]]

        return {
            "genres": [{"id": g.genre_id, "name": g.genre_name} for g in genres],
            "countries": countries,
        }

    def _apply_filters(self, query, filters):
        """Aplikuje filtry do zapytania."""
        from sqlalchemy import func, and_, or_, extract
        from app.models.rating import Rating

        # Filtrowanie po tytule filmu
        if "title" in filters and filters["title"]:
            search_title = f"%{filters['title']}%"
            query = query.filter(Movie.title.ilike(search_title))

        # Filtrowanie po krajach produkcji
        if "countries" in filters and filters["countries"]:
            countries = filters["countries"].split(",")
            query = query.filter(Movie.country.in_(countries))

        # Filtrowanie po latach produkcji
        if "years" in filters and filters["years"]:
            years = filters["years"].split(",")
            year_conditions = []
            for year in years:
                year_conditions.append(extract("year", Movie.release_date) == int(year))
            if year_conditions:
                query = query.filter(or_(*year_conditions))

        # Filtrowanie po gatunkach
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

        # Filtrowanie po minimalnej liczbie ocen
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

        # Filtrowanie po średniej ocenie
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
        """Aplikuje sortowanie do zapytania."""
        from sqlalchemy import func, extract
        from app.models.rating import Rating

        print(f"Sorting by: {sort_by}, order: {sort_order}")

        if sort_by == "average_rating":
            # Sortowanie po średniej ocenie
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
            # Sortowanie po liczbie ocen
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
            # Sortowanie po roku produkcji
            if sort_order.lower() == "asc":
                query = query.order_by(extract("year", Movie.release_date))
            else:
                query = query.order_by(extract("year", Movie.release_date).desc())

        else:
            # Domyślne sortowanie po tytule
            if sort_order.lower() == "asc":
                query = query.order_by(Movie.title)
            else:
                query = query.order_by(Movie.title.desc())

        return query

    def filter_movies(
        self, filters, page=1, per_page=10, sort_by="title", sort_order="asc"
    ):
        """Filtruje filmy na podstawie różnych kryteriów i sortuje wyniki."""
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
