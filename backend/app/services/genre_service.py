from app.repositories.genre_repository import GenreRepository
from app.services.database import db
from app.models.genre import Genre

genre_repo = GenreRepository(db.session)

def get_all_genres():
    try:
        genres = genre_repo.get_all()
        return [genre.serialize() for genre in genres]
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania gatunków: {str(e)}")

def get_genre_by_id(genre_id):
    try:
        genre = genre_repo.get_by_id(genre_id)
        if not genre:
            return None
        return genre.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania gatunku o ID {genre_id}: {str(e)}")

def create_genre(data):
    try:
        genre_name = data.get('name')
        if not genre_name:
            raise ValueError("Nazwa gatunku jest wymagana")
        
        new_genre = Genre(genre_name=genre_name)
        genre_repo.add(new_genre)
        return new_genre.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas tworzenia gatunku: {str(e)}")

def delete_genre(genre_id):
    try:
        success = genre_repo.delete(genre_id)
        return success
    except Exception as e:
        raise Exception(f"Błąd podczas usuwania gatunku o ID {genre_id}: {str(e)}")

def update_genre(genre_id, data):
    try:
        genre_name = data.get('name')
        if not genre_name:
            raise ValueError("Nazwa gatunku jest wymagana")
        
        updated_genre = genre_repo.update(genre_id, genre_name)
        if not updated_genre:
            return None
        return updated_genre.serialize()
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji gatunku o ID {genre_id}: {str(e)}")
