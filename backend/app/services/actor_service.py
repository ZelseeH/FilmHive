from app.repositories.actor_repository import ActorRepository
from app.services.database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import os


class ActorService:
    def __init__(self):
        self.actor_repository = ActorRepository(db.session)

    def get_all_actors(self, page=1, per_page=10):
        result = self.actor_repository.get_all(page, per_page)
        actors = result["actors"]
        pagination = result["pagination"]

        serialized_actors = [actor.serialize() for actor in actors]

        return {"actors": serialized_actors, "pagination": pagination}

    def get_actor_by_id(self, actor_id):
        return self.actor_repository.get_by_id(actor_id)

    def search_actors(self, query, page=1, per_page=10):
        result = self.actor_repository.search(query, page, per_page)
        actors = result["actors"]
        pagination = result["pagination"]

        serialized_actors = [actor.serialize() for actor in actors]

        return {"actors": serialized_actors, "pagination": pagination}

    def add_actor(self, actor_data):
        try:
            # Walidacja wymaganych pól
            if not actor_data.get("name"):
                raise ValueError("Nazwa aktora jest wymagana")

            # Konwersja daty urodzenia
            if (
                "birth_date" in actor_data
                and actor_data["birth_date"]
                and isinstance(actor_data["birth_date"], str)
            ):
                from datetime import datetime

                try:
                    actor_data["birth_date"] = datetime.strptime(
                        actor_data["birth_date"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    raise ValueError(
                        "Nieprawidłowy format daty urodzenia. Użyj formatu YYYY-MM-DD"
                    )

            # POPRAWKA: Walidacja photo_url
            if "photo_url" in actor_data and actor_data["photo_url"]:
                photo_url = actor_data["photo_url"].strip()

                # Sprawdź czy to jest URL (zaczyna się od http)
                if photo_url.startswith(("http://", "https://")):
                    # Walidacja URL-a
                    try:
                        from urllib.parse import urlparse

                        parsed = urlparse(photo_url)
                        if not parsed.netloc:
                            raise ValueError("Nieprawidłowy URL zdjęcia")

                        # Sprawdź czy URL wygląda na zdjęcie
                        valid_extensions = [
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".gif",
                            ".webp",
                            ".svg",
                        ]
                        valid_params = ["image-type", "format=", "media/catalog"]

                        is_valid_image = any(
                            ext in photo_url.lower() for ext in valid_extensions
                        ) or any(param in photo_url.lower() for param in valid_params)

                        if not is_valid_image:
                            current_app.logger.warning(
                                f"URL może nie być obrazem: {photo_url}"
                            )
                            # Nie rzucaj błędu, tylko loguj ostrzeżenie

                        actor_data["photo_url"] = photo_url
                        current_app.logger.info(
                            f"✅ Zaakceptowano photo_url: {photo_url}"
                        )

                    except Exception as e:
                        current_app.logger.error(f"Błąd walidacji URL: {e}")
                        raise ValueError(f"Nieprawidłowy URL zdjęcia: {str(e)}")
                else:
                    # To jest lokalny plik (już uploadowany)
                    current_app.logger.info(f"📁 Lokalny plik photo: {photo_url}")

            # Sprawdź, czy aktor o takiej nazwie już istnieje
            existing_actor = self.actor_repository.get_by_name(actor_data.get("name"))
            if existing_actor:
                raise ValueError(
                    f"Aktor o nazwie '{actor_data.get('name')}' już istnieje"
                )

            # DEBUG: Wyloguj dane przed przekazaniem do repository
            current_app.logger.info(f"📋 Dane aktora do zapisu: {actor_data}")

            new_actor = self.actor_repository.add(actor_data)

            # DEBUG: Wyloguj zapisanego aktora
            current_app.logger.info(
                f"✅ Zapisano aktora: {new_actor.actor_name}, photo_url: {new_actor.photo_url}"
            )

            return new_actor

        except ValueError as e:
            # Przekazujemy błędy walidacji dalej
            raise e
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding actor: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się dodać aktora: {str(e)}")

    def update_actor(self, actor_id, actor_data):
        try:
            # Sprawdź, czy aktor istnieje
            actor = self.actor_repository.get_by_id(actor_id)
            if not actor:
                raise ValueError(f"Aktor o ID {actor_id} nie istnieje")

            print(f"🔄 ActorService.update_actor - dane wejściowe: {actor_data}")

            # Konwersja daty urodzenia
            if (
                "birth_date" in actor_data
                and actor_data["birth_date"]
                and isinstance(actor_data["birth_date"], str)
            ):
                from datetime import datetime

                try:
                    actor_data["birth_date"] = datetime.strptime(
                        actor_data["birth_date"], "%Y-%m-%d"
                    ).date()
                    print(f"📅 Przekonwertowano birth_date: {actor_data['birth_date']}")
                except ValueError:
                    raise ValueError(
                        "Nieprawidłowy format daty urodzenia. Użyj formatu YYYY-MM-DD"
                    )

            # Sprawdź, czy nowa nazwa nie koliduje z istniejącym aktorem
            if "name" in actor_data and actor_data["name"] != actor.actor_name:
                existing_actor = self.actor_repository.get_by_name(actor_data["name"])
                if existing_actor and existing_actor.actor_id != actor_id:
                    raise ValueError(
                        f"Aktor o nazwie '{actor_data['name']}' już istnieje"
                    )

            # POPRAWKA: Walidacja photo_url w update
            if "photo_url" in actor_data and actor_data["photo_url"]:
                photo_url = actor_data["photo_url"].strip()

                # Sprawdź czy to jest URL (zaczyna się od http)
                if photo_url.startswith(("http://", "https://")):
                    # Walidacja URL-a
                    try:
                        from urllib.parse import urlparse

                        parsed = urlparse(photo_url)
                        if not parsed.netloc:
                            raise ValueError("Nieprawidłowy URL zdjęcia")

                        # Sprawdź czy URL wygląda na zdjęcie
                        valid_extensions = [
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".gif",
                            ".webp",
                            ".svg",
                        ]
                        valid_params = ["image-type", "format=", "media/catalog"]

                        is_valid_image = any(
                            ext in photo_url.lower() for ext in valid_extensions
                        ) or any(param in photo_url.lower() for param in valid_params)

                        if not is_valid_image:
                            current_app.logger.warning(
                                f"URL może nie być obrazem: {photo_url}"
                            )

                        actor_data["photo_url"] = photo_url
                        current_app.logger.info(
                            f"✅ Zaakceptowano photo_url w update: {photo_url}"
                        )

                    except Exception as e:
                        current_app.logger.error(f"Błąd walidacji URL w update: {e}")
                        raise ValueError(f"Nieprawidłowy URL zdjęcia: {str(e)}")
                else:
                    # To jest lokalny plik (już uploadowany)
                    current_app.logger.info(
                        f"📁 Lokalny plik photo w update: {photo_url}"
                    )

            # DEBUG: Wyloguj dane przed przekazaniem do repository
            current_app.logger.info(
                f"📋 Dane do aktualizacji w repository: {actor_data}"
            )

            updated_actor = self.actor_repository.update(actor_id, actor_data)

            if updated_actor:
                current_app.logger.info(
                    f"✅ Zaktualizowano aktora: {updated_actor.actor_name}, photo_url: {updated_actor.photo_url}"
                )

            return updated_actor

        except ValueError as e:
            # Przekazujemy błędy walidacji dalej
            current_app.logger.error(f"❌ Błąd walidacji w update_actor: {str(e)}")
            raise e
        except SQLAlchemyError as e:
            current_app.logger.error(f"❌ Error updating actor: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się zaktualizować aktora: {str(e)}")

    def delete_actor(self, actor_id):
        try:
            actor = self.actor_repository.get_by_id(actor_id)
            if not actor:
                raise ValueError(f"Aktor o ID {actor_id} nie istnieje")

            # Sprawdź, czy aktor ma powiązane filmy
            if actor.movies:
                raise ValueError(
                    f"Nie można usunąć aktora '{actor.actor_name}', ponieważ jest powiązany z filmami"
                )

            # Usuń zdjęcie aktora, jeśli istnieje
            if actor.photo_url:
                photo_path = os.path.join(
                    current_app.static_folder, "actors", actor.photo_url
                )
                if os.path.exists(photo_path):
                    os.remove(photo_path)

            return self.actor_repository.delete(actor_id)
        except ValueError as e:
            # Przekazujemy błędy walidacji dalej
            raise e
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error deleting actor: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się usunąć aktora: {str(e)}")

    def get_actor_movies(
        self,
        actor_id,
        page=1,
        per_page=10,
        sort_field="release_date",
        sort_order="desc",
    ):
        """Pobiera filmy aktora z sortowaniem"""
        result = self.actor_repository.get_actor_movies(
            actor_id, page, per_page, sort_field, sort_order
        )
        if not result:
            return None

        movies = result["movies"]
        pagination = result["pagination"]

        serialized_movies = [
            movie.serialize(include_actors=True, include_actors_roles=True)
            for movie in movies
        ]

        for movie_data in serialized_movies:
            if "actors" in movie_data:
                movie_data["actor_role"] = next(
                    (
                        actor["role"]
                        for actor in movie_data["actors"]
                        if actor["id"] == actor_id
                    ),
                    None,
                )
                del movie_data["actors"]

        return {
            "movies": serialized_movies,
            "pagination": pagination,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }

    def upload_actor_photo(self, actor_id, photo_file):
        try:
            if not photo_file:
                raise ValueError("Nie przesłano pliku ze zdjęciem")

            actor = self.actor_repository.get_by_id(actor_id)
            if not actor:
                raise ValueError(f"Aktor o ID {actor_id} nie istnieje")

            if actor.photo_url:
                old_photo_path = os.path.join(
                    current_app.static_folder, "actors", actor.photo_url
                )
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            from werkzeug.utils import secure_filename
            from datetime import datetime

            filename = secure_filename(photo_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"actor_{actor_id}_{timestamp}_{filename}"

            upload_dir = os.path.join(current_app.static_folder, "actors")
            os.makedirs(upload_dir, exist_ok=True)

            photo_path = os.path.join(upload_dir, filename)
            photo_file.save(photo_path)

            return self.actor_repository.update(actor_id, {"photo_url": filename})
        except ValueError as e:
            raise e
        except Exception as e:
            current_app.logger.error(f"Error uploading actor photo: {str(e)}")
            if "photo_path" in locals() and os.path.exists(photo_path):
                os.remove(photo_path)  # Usuń plik, jeśli wystąpił błąd
            raise Exception(f"Nie udało się przesłać zdjęcia aktora: {str(e)}")

    def filter_actors(
        self, filters, page=1, per_page=10, sort_by="name", sort_order="asc"
    ):
        try:
            result = self.actor_repository.filter_actors(
                filters,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            actors = result["actors"]
            pagination = result["pagination"]

            serialized_actors = [actor.serialize() for actor in actors]

            return {
                "actors": serialized_actors,
                "pagination": pagination,
                "sort_by": sort_by,
                "sort_order": sort_order,
            }
        except Exception as e:
            current_app.logger.error(f"Error in filter_actors: {str(e)}")
            raise Exception(f"Błąd podczas filtrowania aktorów: {str(e)}")

    def get_unique_birthplaces(self):
        result = self.actor_repository.get_unique_birthplaces()
        return result

    def search_actors(self, query, page=1, per_page=10):
        result = self.actor_repository.search(query, page, per_page)
        actors = result["actors"]
        pagination = result["pagination"]

        serialized_actors = [actor.serialize() for actor in actors]

        return {"actors": serialized_actors, "pagination": pagination}

        # STATISTICS & DASHBOARD METHODS

    def get_actors_statistics(self):
        """Pobiera statystyki aktorów"""
        try:
            stats = self.actor_repository.get_actors_statistics()
            current_app.logger.info("Retrieved actors statistics")
            return stats
        except Exception as e:
            current_app.logger.error(f"Error getting actors statistics: {str(e)}")
            raise Exception(f"Nie udało się pobrać statystyk aktorów: {str(e)}")

    def get_dashboard_overview(self):
        """Pobiera kompletny przegląd dla dashboard"""
        try:
            dashboard_data = self.actor_repository.get_dashboard_data()
            current_app.logger.info("Retrieved actors dashboard overview")
            return dashboard_data
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard overview: {str(e)}")
            raise Exception(f"Nie udało się pobrać przeglądu dashboard: {str(e)}")

    def get_popular_actors(self, limit=10):
        """Pobiera najpopularniejszych aktorów"""
        try:
            if limit < 1:
                limit = 10
            if limit > 50:
                limit = 50

            popular_actors = self.actor_repository.get_popular_actors(limit)
            current_app.logger.info(f"Retrieved {len(popular_actors)} popular actors")
            return {"actors": popular_actors, "total_returned": len(popular_actors)}
        except Exception as e:
            current_app.logger.error(f"Error getting popular actors: {str(e)}")
            raise Exception(f"Nie udało się pobrać popularnych aktorów: {str(e)}")

    def get_actors_by_country(self):
        """Pobiera statystyki według krajów"""
        try:
            country_stats = self.actor_repository.get_actors_by_country()
            current_app.logger.info("Retrieved actors statistics by country")
            return {"countries": country_stats, "total_countries": len(country_stats)}
        except Exception as e:
            current_app.logger.error(f"Error getting actors by country: {str(e)}")
            raise Exception(f"Nie udało się pobrać statystyk według krajów: {str(e)}")

    def get_age_distribution(self):
        """Pobiera rozkład wieku aktorów"""
        try:
            age_distribution = self.actor_repository.get_age_distribution()
            current_app.logger.info("Retrieved actors age distribution")
            return {
                "age_ranges": age_distribution,
                "total_with_age_data": sum(item["count"] for item in age_distribution),
            }
        except Exception as e:
            current_app.logger.error(f"Error getting age distribution: {str(e)}")
            raise Exception(f"Nie udało się pobrać rozkładu wieku: {str(e)}")

    def get_recent_actors(self, limit=5):
        """Pobiera ostatnio dodanych aktorów"""
        try:
            if limit < 1:
                limit = 5
            if limit > 20:
                limit = 20

            recent_actors = self.actor_repository.get_recent_actors(limit)
            current_app.logger.info(f"Retrieved {len(recent_actors)} recent actors")
            return {"actors": recent_actors, "total_returned": len(recent_actors)}
        except Exception as e:
            current_app.logger.error(f"Error getting recent actors: {str(e)}")
            raise Exception(f"Nie udało się pobrać ostatnich aktorów: {str(e)}")
