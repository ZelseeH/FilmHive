from app.models.actor import Actor
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_


class ActorRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self, page=1, per_page=10):
        """Pobiera wszystkich aktorów z paginacją."""
        total = self.session.query(Actor).count()
        actors = (
            self.session.query(Actor)
            .order_by(Actor.actor_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "actors": actors,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def get_by_id(self, actor_id):
        """Pobiera aktora na podstawie ID."""
        return self.session.query(Actor).filter(Actor.actor_id == actor_id).first()

    def search(self, query, page=1, per_page=10):
        """Wyszukuje aktorów na podstawie zapytania."""
        search_query = f"%{query}%"
        total = (
            self.session.query(Actor)
            .filter(
                or_(
                    Actor.actor_name.ilike(search_query),
                    Actor.biography.ilike(search_query),
                )
            )
            .count()
        )

        actors = (
            self.session.query(Actor)
            .filter(
                or_(
                    Actor.actor_name.ilike(search_query),
                    Actor.biography.ilike(search_query),
                )
            )
            .order_by(Actor.actor_name)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "actors": actors,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def add(self, actor_data):
        """Dodaje nowego aktora."""
        try:
            actor = Actor(
                actor_name=actor_data.get("name"),
                birth_date=actor_data.get("birth_date"),
                birth_place=actor_data.get("birth_place"),
                biography=actor_data.get("biography"),
                photo_url=actor_data.get("photo_url"),
            )
            self.session.add(actor)
            self.session.commit()
            return actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update(self, actor_id, actor_data):
        """Aktualizuje dane aktora."""
        try:
            actor = self.get_by_id(actor_id)
            if not actor:
                return None

            if "name" in actor_data:
                actor.actor_name = actor_data["name"]
            if "birth_date" in actor_data:
                actor.birth_date = actor_data["birth_date"]
            if "birth_place" in actor_data:
                actor.birth_place = actor_data["birth_place"]
            if "biography" in actor_data:
                actor.biography = actor_data["biography"]
            if "photo_url" in actor_data:
                actor.photo_url = actor_data["photo_url"]

            self.session.commit()
            return actor
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete(self, actor_id):
        """Usuwa aktora."""
        try:
            actor = self.get_by_id(actor_id)
            if not actor:
                return False

            self.session.delete(actor)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_actor_movies(self, actor_id, page=1, per_page=10):
        """Pobiera filmy, w których wystąpił aktor."""
        actor = self.get_by_id(actor_id)
        if not actor:
            return None

        total = len(actor.movies)
        movies = actor.movies[(page - 1) * per_page : page * per_page]

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
