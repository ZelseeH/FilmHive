from app.repositories.director_repository import DirectorRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import os


class DirectorService:
    def __init__(self):
        self.director_repository = DirectorRepository(db.session)

    def get_all_directors(self, page=1, per_page=10):
        result = self.director_repository.get_all(page, per_page)
        directors = result["directors"]
        pagination = result["pagination"]

        serialized_directors = [director.serialize() for director in directors]

        return {"directors": serialized_directors, "pagination": pagination}

    def get_director_by_id(self, director_id):
        return self.director_repository.get_by_id(director_id)

    def search_directors(self, query, page=1, per_page=10):
        result = self.director_repository.search(query, page, per_page)
        directors = result["directors"]
        pagination = result["pagination"]

        serialized_directors = [director.serialize() for director in directors]

        return {"directors": serialized_directors, "pagination": pagination}

    def add_director(self, director_data):
        try:
            return self.director_repository.add(director_data)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding director: {str(e)}")
            raise Exception("Failed to add director")

    def update_director(self, director_id, director_data):
        try:
            return self.director_repository.update(director_id, director_data)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error updating director: {str(e)}")
            raise Exception("Failed to update director")

    def delete_director(self, director_id):
        try:
            director = self.director_repository.get_by_id(director_id)
            if director and director.photo_url:
                photo_path = os.path.join(
                    current_app.static_folder, "directors", director.photo_url
                )
                if os.path.exists(photo_path):
                    os.remove(photo_path)

            return self.director_repository.delete(director_id)
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error deleting director: {str(e)}")
            raise Exception("Failed to delete director")

    def get_director_movies(self, director_id, page=1, per_page=10):
        result = self.director_repository.get_director_movies(
            director_id, page, per_page
        )
        if not result:
            return None

        movies = result["movies"]
        pagination = result["pagination"]

        serialized_movies = [
            movie.serialize(include_directors=True) for movie in movies
        ]

        return {"movies": serialized_movies, "pagination": pagination}

    def upload_director_photo(self, director_id, photo_file):
        try:
            director = self.director_repository.get_by_id(director_id)
            if not director:
                return None
            if director.photo_url:
                old_photo_path = os.path.join(
                    current_app.static_folder, "directors", director.photo_url
                )
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            filename = f"director_{director_id}_{photo_file.filename}"
            photo_path = os.path.join(current_app.static_folder, "directors", filename)

            os.makedirs(os.path.dirname(photo_path), exist_ok=True)

            photo_file.save(photo_path)

            director = self.director_repository.update(
                director_id, {"photo_url": filename}
            )
            return director
        except Exception as e:
            current_app.logger.error(f"Error uploading director photo: {str(e)}")
            raise Exception("Failed to upload director photo")
