import time
import requests
import sys
from app import create_app
from app.extensions import db
from app.models.actor import Actor

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"

spinner = ["-", "\\", "|", "/"]


def get_popular_actors(page):
    url = f"{base_url}/person/popular"
    params = {
        "api_key": api_key,
        "language": language,
        "page": page,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_actor_details(actor_id):
    url = f"{base_url}/person/{actor_id}"
    params = {"api_key": api_key, "language": language}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def sanitize(text):
    if text is None:
        return ""
    return text.replace("\n", " ").replace("\r", " ").replace("'", "''").strip()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        actors_to_add = []
        actors_fetched = 0
        max_actors = 1000
        current_page = 50
        max_pages = 440
        spin_idx = 0

        while actors_fetched < max_actors and current_page <= max_pages:
            data = get_popular_actors(current_page)
            results = data.get("results", [])

            for person in results:
                if actors_fetched >= max_actors:
                    break

                known_for = person.get("known_for_department")
                if known_for != "Acting":
                    continue

                actor_id = person["id"]
                details = get_actor_details(actor_id)
                actor_name = details.get("name")

                existing_actor = Actor.query.filter_by(actor_name=actor_name).first()
                if existing_actor:
                    continue

                birth_date = details.get("birthday")
                birth_place = details.get("place_of_birth")
                biography = details.get("biography")
                profile_path = details.get("profile_path")
                photo_url = (
                    f"https://image.tmdb.org/t/p/w500{profile_path}"
                    if profile_path
                    else ""
                )
                gender_code = details.get("gender", 0)
                gender = "K" if gender_code == 1 else "M" if gender_code == 2 else ""

                if not all([birth_date, birth_place, biography, photo_url, gender]):
                    continue

                actor_name = sanitize(actor_name)
                birth_place = sanitize(birth_place)
                biography = sanitize(biography)

                actor_obj = Actor(
                    actor_name=actor_name,
                    birth_date=birth_date,
                    birth_place=birth_place,
                    biography=biography,
                    photo_url=photo_url,
                    gender=gender,
                )

                actors_to_add.append(actor_obj)
                actors_fetched += 1

                sys.stdout.write(
                    f"\rAktualnie przetworzono aktorów: {actors_fetched} {spinner[spin_idx % len(spinner)]}"
                )
                sys.stdout.flush()
                spin_idx += 1

                time.sleep(0.05)

            current_page += 1

        print("\nImport zakończony.")

        if actors_to_add:
            try:
                db.session.add_all(actors_to_add)
                db.session.commit()
                print(f"Dodano {len(actors_to_add)} aktorów do bazy jednorazowo.")
            except Exception as e:
                db.session.rollback()
                print(f"Błąd przy dodawaniu aktorów: {str(e)}")
        else:
            print("Brak aktorów do dodania.")
