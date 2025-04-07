from app.repositories.actor_repository import ActorRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import os


class ActorService:
    def __init__(self):
        self.actor_repository = ActorRepository(db.session)

    def get_all_actors(self, page=1, per_page=10):
        """Pobiera wszystkich aktorów z paginacją."""
        result = self.actor_repository.get_all(page, per_page)
        actors = result["actors"]
        pagination = result["pagination"]

        serialized_actors = [actor.serialize() for actor in actors]

        return {"actors": serialized_actors, "pagination": pagination}

    def get_actor_by_id(self, actor_id):
        """Pobiera aktora na podstawie ID."""
        return self.actor_repository.get_by_id(actor_id)

    def search_actors(self, query, page=1, per_page=10):
        """Wyszukuje aktorów na podstawie zapytania."""
        result = self.actor_repository.search(query, page, per_page)
        actors = result["actors"]
        pagination = result["pagination"]

        serialized_actors = [actor.serialize() for actor in actors]

        return {"actors": serialized_actors, "pagination": pagination}

    def add_actor(self, actor_data):
        """Dodaje nowego aktora."""
        try:
            return self.actor_repository.add(actor_data)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding actor: {str(e)}")
            raise Exception("Failed to add actor")

    def update_actor(self, actor_id, actor_data):
        """Aktualizuje dane aktora."""
        try:
            return self.actor_repository.update(actor_id, actor_data)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error updating actor: {str(e)}")
            raise Exception("Failed to update actor")

    def delete_actor(self, actor_id):
        """Usuwa aktora."""
        try:
            actor = self.actor_repository.get_by_id(actor_id)
            if actor and actor.photo_url:
                photo_path = os.path.join(
                    current_app.static_folder, "actors", actor.photo_url
                )
                if os.path.exists(photo_path):
                    os.remove(photo_path)

            return self.actor_repository.delete(actor_id)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error deleting actor: {str(e)}")
            raise Exception("Failed to delete actor")

    def get_actor_movies(self, actor_id, page=1, per_page=10):
        """Pobiera filmy, w których wystąpił aktor."""
        result = self.actor_repository.get_actor_movies(actor_id, page, per_page)
        if not result:
            return None

        movies = result["movies"]
        pagination = result["pagination"]

        serialized_movies = [movie.serialize() for movie in movies]

        return {"movies": serialized_movies, "pagination": pagination}

    def upload_actor_photo(self, actor_id, photo_file):
        """Zapisuje zdjęcie aktora."""
        try:
            actor = self.actor_repository.get_by_id(actor_id)
            if not actor:
                return None
            if actor.photo_url:
                old_photo_path = os.path.join(
                    current_app.static_folder, "actors", actor.photo_url
                )
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            filename = f"actor_{actor_id}_{photo_file.filename}"
            photo_path = os.path.join(current_app.static_folder, "actors", filename)

            os.makedirs(os.path.dirname(photo_path), exist_ok=True)

            photo_file.save(photo_path)

            actor = self.actor_repository.update(actor_id, {"photo_url": filename})
            return actor
        except Exception as e:
            current_app.logger.error(f"Error uploading actor photo: {str(e)}")
            raise Exception("Failed to upload actor photo")

    def filter_actors(self, filters, page=1, per_page=10):
        """Filtruje aktorów na podstawie różnych kryteriów."""
        result = self.actor_repository.filter_actors(filters, page, per_page)
        actors = result["actors"]
        pagination = result["pagination"]

        serialized_actors = [actor.serialize() for actor in actors]

        return {"actors": serialized_actors, "pagination": pagination}

    def get_unique_birthplaces(self):
        """Pobiera unikalne miejsca urodzenia aktorów."""
        result = self.actor_repository.get_unique_birthplaces()
        return result
