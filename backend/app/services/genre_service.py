from app.repositories.genre_repository import GenreRepository
from app.services.database import db
from app.models.genre import Genre

genre_repo = GenreRepository(db.session)


def get_all_genres():
    try:
        genres = genre_repo.get_all()
        return genres  # <-- zwracaj listę obiektów Genre, nie słowniki!
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania gatunków: {str(e)}")


def get_genre_by_id(genre_id):
    try:
        genre = genre_repo.get_by_id(genre_id)
        return genre  # <-- zwracaj obiekt Genre lub None
    except Exception as e:
        raise Exception(f"Błąd podczas pobierania gatunku o ID {genre_id}: {str(e)}")


def create_genre(data):
    try:
        genre_name = data.get("name")
        if not genre_name:
            raise ValueError("Nazwa gatunku jest wymagana")

        new_genre = Genre(genre_name=genre_name)
        genre_repo.add(new_genre)
        return new_genre  # <-- zwracaj obiekt Genre
    except Exception as e:
        raise Exception(f"Błąd podczas tworzenia gatunku: {str(e)}")


def delete_genre(genre_id):
    try:
        success = genre_repo.delete(genre_id)
        return success  # <-- zwracaj True/False
    except Exception as e:
        raise Exception(f"Błąd podczas usuwania gatunku o ID {genre_id}: {str(e)}")


def update_genre(genre_id, data):
    try:
        genre_name = data.get("name")
        if not genre_name:
            raise ValueError("Nazwa gatunku jest wymagana")

        updated_genre = genre_repo.update(genre_id, genre_name)
        return updated_genre  # <-- zwracaj obiekt Genre lub None
    except Exception as e:
        raise Exception(f"Błąd podczas aktualizacji gatunku o ID {genre_id}: {str(e)}")
