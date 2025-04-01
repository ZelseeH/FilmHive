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
        
        # Filtrowanie po gatunku, jeśli podano
        if genre_id:
            query = query.join(Movie.genres).filter(Genre.genre_id == genre_id)
        
        # Obliczanie offsetu na podstawie strony
        offset = (page - 1) * per_page
        
        # Pobieranie całkowitej liczby filmów (dla metadanych paginacji)
        total = query.count()
        
        # Pobieranie filmów dla bieżącej strony
        movies = query.order_by(Movie.title).offset(offset).limit(per_page).all()
        
        # Obliczanie całkowitej liczby stron
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "movies": movies,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
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
