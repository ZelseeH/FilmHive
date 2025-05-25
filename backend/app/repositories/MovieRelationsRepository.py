from sqlalchemy.exc import SQLAlchemyError
from app.models.movie_actor import MovieActor
from app.models.movie_director import MovieDirector
from app.models.movie_genre import MovieGenre
from app.models.movie import Movie
from app.models.actor import Actor
from app.models.director import Director
from app.models.genre import Genre


class MovieRelationsRepository:
    def __init__(self, session):
        self.session = session

    def add_actor_to_movie(self, movie_id, actor_id, role=None):
        try:
            existing = (
                self.session.query(MovieActor)
                .filter(
                    MovieActor.movie_id == movie_id, MovieActor.actor_id == actor_id
                )
                .first()
            )

            if existing:
                raise ValueError("Aktor już jest przypisany do tego filmu")

            movie_actor = MovieActor(
                movie_id=movie_id, actor_id=actor_id, movie_role=role or ""
            )
            self.session.add(movie_actor)
            self.session.commit()
            return movie_actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def remove_actor_from_movie(self, movie_id, actor_id):
        try:
            movie_actor = (
                self.session.query(MovieActor)
                .filter(
                    MovieActor.movie_id == movie_id, MovieActor.actor_id == actor_id
                )
                .first()
            )

            if not movie_actor:
                return False

            self.session.delete(movie_actor)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def add_director_to_movie(self, movie_id, director_id):
        try:
            existing = (
                self.session.query(MovieDirector)
                .filter(
                    MovieDirector.movie_id == movie_id,
                    MovieDirector.director_id == director_id,
                )
                .first()
            )

            if existing:
                raise ValueError("Reżyser już jest przypisany do tego filmu")

            movie_director = MovieDirector(movie_id=movie_id, director_id=director_id)
            self.session.add(movie_director)
            self.session.commit()
            return movie_director
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def remove_director_from_movie(self, movie_id, director_id):
        try:
            movie_director = (
                self.session.query(MovieDirector)
                .filter(
                    MovieDirector.movie_id == movie_id,
                    MovieDirector.director_id == director_id,
                )
                .first()
            )

            if not movie_director:
                return False

            self.session.delete(movie_director)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def add_genre_to_movie(self, movie_id, genre_id):
        try:
            existing = (
                self.session.query(MovieGenre)
                .filter(
                    MovieGenre.movie_id == movie_id, MovieGenre.genre_id == genre_id
                )
                .first()
            )

            if existing:
                raise ValueError("Gatunek już jest przypisany do tego filmu")

            movie_genre = MovieGenre(movie_id=movie_id, genre_id=genre_id)
            self.session.add(movie_genre)
            self.session.commit()
            return movie_genre
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def remove_genre_from_movie(self, movie_id, genre_id):
        try:
            movie_genre = (
                self.session.query(MovieGenre)
                .filter(
                    MovieGenre.movie_id == movie_id, MovieGenre.genre_id == genre_id
                )
                .first()
            )

            if not movie_genre:
                return False

            self.session.delete(movie_genre)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_movie_actors(self, movie_id):
        try:
            return (
                self.session.query(MovieActor)
                .join(Actor)
                .filter(MovieActor.movie_id == movie_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_movie_directors(self, movie_id):
        try:
            return (
                self.session.query(MovieDirector)
                .join(Director)
                .filter(MovieDirector.movie_id == movie_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_movie_genres(self, movie_id):
        try:
            return (
                self.session.query(MovieGenre)
                .join(Genre)
                .filter(MovieGenre.movie_id == movie_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
