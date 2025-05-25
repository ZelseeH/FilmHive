from app.repositories.MovieRelationsRepository import MovieRelationsRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app


class MovieRelationsService:
    def __init__(self):
        self.movie_relations_repository = MovieRelationsRepository(db.session)

    def add_actor_to_movie(self, movie_id, actor_id, role=None):
        try:
            return self.movie_relations_repository.add_actor_to_movie(
                movie_id, actor_id, role
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding actor to movie: {str(e)}")
            raise Exception("Failed to add actor to movie")

    def remove_actor_from_movie(self, movie_id, actor_id):
        try:
            return self.movie_relations_repository.remove_actor_from_movie(
                movie_id, actor_id
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error removing actor from movie: {str(e)}")
            raise Exception("Failed to remove actor from movie")

    def add_director_to_movie(self, movie_id, director_id):
        try:
            return self.movie_relations_repository.add_director_to_movie(
                movie_id, director_id
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding director to movie: {str(e)}")
            raise Exception("Failed to add director to movie")

    def remove_director_from_movie(self, movie_id, director_id):
        try:
            return self.movie_relations_repository.remove_director_from_movie(
                movie_id, director_id
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error removing director from movie: {str(e)}")
            raise Exception("Failed to remove director from movie")

    def add_genre_to_movie(self, movie_id, genre_id):
        try:
            return self.movie_relations_repository.add_genre_to_movie(
                movie_id, genre_id
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding genre to movie: {str(e)}")
            raise Exception("Failed to add genre to movie")

    def remove_genre_from_movie(self, movie_id, genre_id):
        try:
            return self.movie_relations_repository.remove_genre_from_movie(
                movie_id, genre_id
            )
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error removing genre from movie: {str(e)}")
            raise Exception("Failed to remove genre from movie")

    def get_movie_actors(self, movie_id):
        try:
            movie_actors = self.movie_relations_repository.get_movie_actors(movie_id)
            return [
                {
                    "actor_id": ma.actor_id,
                    "actor_name": ma.actor.actor_name if hasattr(ma, "actor") else None,
                    "role": ma.movie_role,
                }
                for ma in movie_actors
            ]
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting movie actors: {str(e)}")
            raise Exception("Failed to get movie actors")

    def get_movie_directors(self, movie_id):
        try:
            movie_directors = self.movie_relations_repository.get_movie_directors(
                movie_id
            )
            return [
                {
                    "director_id": md.director_id,
                    "director_name": (
                        md.director.director_name if hasattr(md, "director") else None
                    ),
                }
                for md in movie_directors
            ]
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting movie directors: {str(e)}")
            raise Exception("Failed to get movie directors")

    def get_movie_genres(self, movie_id):
        try:
            movie_genres = self.movie_relations_repository.get_movie_genres(movie_id)
            return [
                {
                    "genre_id": mg.genre_id,
                    "genre_name": mg.genre.genre_name if hasattr(mg, "genre") else None,
                }
                for mg in movie_genres
            ]
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting movie genres: {str(e)}")
            raise Exception("Failed to get movie genres")
