import time
import requests
import sys
import os
import logging
import string

# Disable DEBUG logs
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# FIX: Add backend to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
backend_dir = os.path.dirname(app_dir)
sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from app.models.actor import Actor

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"


def get_popular_actors(page):
    """Get popular actors"""
    url = f"{base_url}/person/popular"
    params = {
        "api_key": api_key,
        "language": language,
        "page": page,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_actor_details(actor_id):
    url = f"{base_url}/person/{actor_id}"
    params = {"api_key": api_key, "language": language}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def sanitize(text):
    if text is None:
        return ""
    return text.replace("\n", " ").replace("\r", " ").replace("'", "''").strip()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        max_pages_per_letter = 50

        # Letters A-Z
        search_letters = list(string.ascii_uppercase)  # ['A', 'B', ..., 'Z']

        print("🎬 ROZPOCZYNAM IMPORT AKTORÓW Z TMDb")
        print(f"📊 Cel: {len(search_letters)} liter × {max_pages_per_letter} stron")
        print("=" * 80)

        total_actors_all = 0
        total_letters = len(search_letters)

        try:
            for letter_idx, target_letter in enumerate(search_letters):
                print(f"\n{'='*80}")
                print(f"🔤 LITERA {letter_idx + 1}/{total_letters}: '{target_letter}'")
                print(f"{'='*80}")

                # Start from page based on letter (A=1-50, B=51-100, etc.)
                start_page = 1 + (letter_idx * max_pages_per_letter)
                end_page = start_page + max_pages_per_letter

                actors_this_letter = 0

                for relative_page in range(1, max_pages_per_letter + 1):
                    absolute_page = start_page + relative_page - 1
                    actors_to_add = []  # Buffer dla current page

                    try:
                        data = get_popular_actors(absolute_page)
                        results = data.get("results", [])

                        if not results:
                            print(
                                f"   📄 {relative_page}/{max_pages_per_letter} - Brak wyników (KONIEC)"
                            )
                            break

                        for person in results:
                            known_for = person.get("known_for_department")
                            if known_for != "Acting":
                                continue

                            actor_id = person["id"]
                            actor_name = person.get("name", "")

                            # Filter: only target_letter
                            if not actor_name or not actor_name.upper().startswith(
                                target_letter
                            ):
                                continue

                            # Check duplicate
                            existing_actor = Actor.query.filter_by(
                                actor_name=actor_name
                            ).first()
                            if existing_actor:
                                continue

                            # Get details
                            try:
                                details = get_actor_details(actor_id)
                            except Exception:
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
                            gender = (
                                "K"
                                if gender_code == 1
                                else "M" if gender_code == 2 else ""
                            )

                            # Skip incomplete
                            if not all(
                                [birth_date, birth_place, biography, photo_url, gender]
                            ):
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

                            time.sleep(0.05)

                        # Save po każdej stronie
                        if actors_to_add:
                            try:
                                db.session.add_all(actors_to_add)
                                db.session.commit()
                                actors_this_letter += len(actors_to_add)
                                total_actors_all += len(actors_to_add)
                                print(
                                    f"   📄 {relative_page}/{max_pages_per_letter} - Dodano {len(actors_to_add)} aktorów ✅"
                                )
                            except Exception as e:
                                db.session.rollback()
                                print(
                                    f"   📄 {relative_page}/{max_pages_per_letter} - Błąd zapisu: {e} ❌"
                                )
                        else:
                            print(
                                f"   📄 {relative_page}/{max_pages_per_letter} - Brak nowych aktorów (skip)"
                            )

                        time.sleep(0.3)  # Rate limit

                    except requests.RequestException as e:
                        print(
                            f"   📄 {relative_page}/{max_pages_per_letter} - Błąd HTTP: {e} ⚠️"
                        )
                        time.sleep(5)
                        continue

                    except Exception as e:
                        print(
                            f"   📄 {relative_page}/{max_pages_per_letter} - Błąd: {e} ⚠️"
                        )
                        continue

                print(
                    f"\n✅ Litera '{target_letter}' zakończona: {actors_this_letter} aktorów (TOTAL: {total_actors_all})"
                )

        except KeyboardInterrupt:
            print("\n\n⚠️  PRZERWANO (Ctrl+C)")
            print(f"📊 TOTAL zapisanych aktorów: {total_actors_all}")

        print(f"\n{'='*80}")
        print(f"🎉 IMPORT ZAKOŃCZONY!")
        print(f"{'='*80}")
        print(f"📊 TOTAL aktorów dodanych: {total_actors_all}")
