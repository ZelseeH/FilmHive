from app.repositories.movie_repository import MovieRepository
from app.services.database import db
from app.models.movie import Movie

# Inicjalizacja repozytorium
movie_repo = MovieRepository(db.session)

def get_all_movies():
    """Pobiera wszystkie filmy i serializuje je."""
    try:
        movies = movie_repo.get_all()
        return [movie.serialize() for movie in movies]
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmów: {str(e)}")

def get_movie_by_id(movie_id):
    """Pobiera film na podstawie ID i serializuje go."""
    try:
        movie = movie_repo.get_by_id(movie_id)
        if not movie:
            return None
        return movie.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania filmu o ID {movie_id}: {str(e)}")

def create_movie(data):
    """Tworzy nowy film na podstawie danych wejściowych."""
    try:
        new_movie = Movie(
            title=data.get('title'),
            release_date=data.get('release_date'),
            description=data.get('description', ''),  # Domyślnie pusty opis
            poster_url=data.get('poster_url', ''),   # Domyślnie brak URL
            duration_minutes=data.get('duration_minutes', 0),  # Domyślna długość 0
            country=data.get('country', ''),         # Domyślnie brak kraju
            original_language=data.get('original_language', '')  # Domyślnie brak języka
        )
        movie_repo.add(new_movie)
        return new_movie.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas tworzenia filmu: {str(e)}")

def delete_movie(movie_id):
    """Usuwa film na podstawie ID."""
    try:
        success = movie_repo.delete(movie_id)
        return success
    except Exception as e:
        raise Exception(f"Błąd podczas usuwania filmu o ID {movie_id}: {str(e)}")
