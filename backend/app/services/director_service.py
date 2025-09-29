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
            # Walidacja wymaganych pól
            if not director_data.get("name"):
                raise ValueError("Nazwa reżysera jest wymagana")

            # Konwersja daty urodzenia
            if (
                "birth_date" in director_data
                and director_data["birth_date"]
                and isinstance(director_data["birth_date"], str)
            ):
                from datetime import datetime

                try:
                    director_data["birth_date"] = datetime.strptime(
                        director_data["birth_date"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    raise ValueError(
                        "Nieprawidłowy format daty urodzenia. Użyj formatu YYYY-MM-DD"
                    )

            # POPRAWKA: Walidacja photo_url
            if "photo_url" in director_data and director_data["photo_url"]:
                photo_url = director_data["photo_url"].strip()

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
                                f"URL może nie być obrazem (reżyser): {photo_url}"
                            )

                        director_data["photo_url"] = photo_url
                        current_app.logger.info(
                            f"✅ Zaakceptowano photo_url dla reżysera: {photo_url}"
                        )

                    except Exception as e:
                        current_app.logger.error(f"Błąd walidacji URL reżysera: {e}")
                        raise ValueError(f"Nieprawidłowy URL zdjęcia: {str(e)}")
                else:
                    # To jest lokalny plik (już uploadowany)
                    current_app.logger.info(
                        f"📁 Lokalny plik photo reżysera: {photo_url}"
                    )

            # Sprawdź, czy reżyser o takiej nazwie już istnieje
            existing_director = self.director_repository.get_by_name(
                director_data.get("name")
            )
            if existing_director:
                raise ValueError(
                    f"Reżyser o nazwie '{director_data.get('name')}' już istnieje"
                )

            # DEBUG: Wyloguj dane przed przekazaniem do repository
            current_app.logger.info(f"📋 Dane reżysera do zapisu: {director_data}")

            new_director = self.director_repository.add(director_data)

            # DEBUG: Wyloguj zapisanego reżysera
            current_app.logger.info(
                f"✅ Zapisano reżysera: {new_director.director_name}, photo_url: {new_director.photo_url}"
            )

            return new_director

        except ValueError as e:
            # Przekazujemy błędy walidacji dalej
            raise e
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding director: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się dodać reżysera: {str(e)}")

    def update_director(self, director_id, director_data):
        try:
            # Sprawdź, czy reżyser istnieje
            director = self.director_repository.get_by_id(director_id)
            if not director:
                raise ValueError(f"Reżyser o ID {director_id} nie istnieje")

            current_app.logger.info(
                f"🔄 DirectorService.update_director - dane wejściowe: {director_data}"
            )

            # Konwersja daty urodzenia
            if (
                "birth_date" in director_data
                and director_data["birth_date"]
                and isinstance(director_data["birth_date"], str)
            ):
                from datetime import datetime

                try:
                    director_data["birth_date"] = datetime.strptime(
                        director_data["birth_date"], "%Y-%m-%d"
                    ).date()
                    current_app.logger.info(
                        f"📅 Przekonwertowano birth_date: {director_data['birth_date']}"
                    )
                except ValueError:
                    raise ValueError(
                        "Nieprawidłowy format daty urodzenia. Użyj formatu YYYY-MM-DD"
                    )

            # Sprawdź, czy nowa nazwa nie koliduje z istniejącym reżyserem
            if (
                "name" in director_data
                and director_data["name"] != director.director_name
            ):
                existing_director = self.director_repository.get_by_name(
                    director_data["name"]
                )
                if existing_director and existing_director.director_id != director_id:
                    raise ValueError(
                        f"Reżyser o nazwie '{director_data['name']}' już istnieje"
                    )

            # POPRAWKA: Walidacja photo_url w update
            if "photo_url" in director_data and director_data["photo_url"]:
                photo_url = director_data["photo_url"].strip()

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
                                f"URL może nie być obrazem (reżyser): {photo_url}"
                            )

                        director_data["photo_url"] = photo_url
                        current_app.logger.info(
                            f"✅ Zaakceptowano photo_url w update reżysera: {photo_url}"
                        )

                    except Exception as e:
                        current_app.logger.error(
                            f"Błąd walidacji URL w update reżysera: {e}"
                        )
                        raise ValueError(f"Nieprawidłowy URL zdjęcia: {str(e)}")
                else:
                    # To jest lokalny plik (już uploadowany)
                    current_app.logger.info(
                        f"📁 Lokalny plik photo w update reżysera: {photo_url}"
                    )

            # DEBUG: Wyloguj dane przed przekazaniem do repository
            current_app.logger.info(
                f"📋 Dane do aktualizacji reżysera w repository: {director_data}"
            )

            updated_director = self.director_repository.update(
                director_id, director_data
            )

            if updated_director:
                current_app.logger.info(
                    f"✅ Zaktualizowano reżysera: {updated_director.director_name}, photo_url: {updated_director.photo_url}"
                )

            return updated_director

        except ValueError as e:
            # Przekazujemy błędy walidacji dalej
            current_app.logger.error(f"❌ Błąd walidacji w update_director: {str(e)}")
            raise e
        except SQLAlchemyError as e:
            current_app.logger.error(f"❌ Error updating director: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się zaktualizować reżysera: {str(e)}")

    def delete_director(self, director_id):
        try:
            director = self.director_repository.get_by_id(director_id)
            if not director:
                raise ValueError(f"Reżyser o ID {director_id} nie istnieje")

            # Sprawdź, czy reżyser ma powiązane filmy
            if director.movies:
                raise ValueError(
                    f"Nie można usunąć reżysera '{director.director_name}', ponieważ jest powiązany z filmami"
                )

            # Usuń zdjęcie reżysera, jeśli istnieje i nie jest URL-em
            if director.photo_url and not director.photo_url.startswith("http"):
                photo_path = os.path.join(
                    current_app.static_folder, "directors", director.photo_url
                )
                if os.path.exists(photo_path):
                    os.remove(photo_path)

            return self.director_repository.delete(director_id)

        except ValueError as e:
            # Przekazujemy błędy walidacji dalej
            raise e
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error deleting director: {str(e)}")
            db.session.rollback()
            raise Exception(f"Nie udało się usunąć reżysera: {str(e)}")

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
            if not photo_file:
                raise ValueError("Nie przesłano pliku ze zdjęciem")

            director = self.director_repository.get_by_id(director_id)
            if not director:
                raise ValueError(f"Reżyser o ID {director_id} nie istnieje")

            # Usuń stare zdjęcie jeśli było lokalne
            if director.photo_url and not director.photo_url.startswith("http"):
                old_photo_path = os.path.join(
                    current_app.static_folder, "directors", director.photo_url
                )
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            from werkzeug.utils import secure_filename
            from datetime import datetime

            filename = secure_filename(photo_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"director_{director_id}_{timestamp}_{filename}"

            upload_dir = os.path.join(current_app.static_folder, "directors")
            os.makedirs(upload_dir, exist_ok=True)

            photo_path = os.path.join(upload_dir, filename)
            photo_file.save(photo_path)

            return self.director_repository.update(director_id, {"photo_url": filename})

        except ValueError as e:
            raise e
        except Exception as e:
            current_app.logger.error(f"Error uploading director photo: {str(e)}")
            if "photo_path" in locals() and os.path.exists(photo_path):
                os.remove(photo_path)  # Usuń plik, jeśli wystąpił błąd
            raise Exception(f"Nie udało się przesłać zdjęcia reżysera: {str(e)}")

    def get_basic_statistics(self):
        """Pobiera podstawowe statystyki reżyserów"""
        try:
            stats = self.director_repository.get_basic_statistics()
            current_app.logger.info("Retrieved basic directors statistics")
            return stats
        except Exception as e:
            current_app.logger.error(f"Error getting basic statistics: {str(e)}")
            raise Exception(f"Nie udało się pobrać statystyk: {str(e)}")

    def get_dashboard_data(self):
        """Pobiera dane dashboard dla reżyserów"""
        try:
            dashboard_data = self.director_repository.get_dashboard_data()
            current_app.logger.info("Retrieved directors dashboard data")
            return dashboard_data
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard data: {str(e)}")
            raise Exception(f"Nie udało się pobrać danych dashboard: {str(e)}")
