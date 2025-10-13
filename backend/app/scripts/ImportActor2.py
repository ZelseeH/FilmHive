import time
import requests
import sys
import os
import logging
import string

# Disable DEBUG logs
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

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


def search_actors_by_letter(letter, page):
    """Search actors by first letter"""
    url = f"{base_url}/search/person"
    params = {
        "api_key": api_key,
        "language": language,
        "query": letter,  # Single letter search
        "page": page,
        "include_adult": False,
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
        max_pages_per_letter = 20  # Search API usually has fewer pages per letter

        # Common first names (A-Z) - better than single letters
        search_queries = [
            # A
            "Adam",
            "Anna",
            "Andrew",
            "Amy",
            "Anthony",
            "Alice",
            # B
            "Brad",
            "Ben",
            "Brian",
            "Bruce",
            "Bill",
            "Barbara",
            # C
            "Chris",
            "Cate",
            "Colin",
            "Cameron",
            "Charlie",
            "Catherine",
            # D
            "Daniel",
            "David",
            "Denzel",
            "Dakota",
            "Dwayne",
            "Drew",
            # E
            "Emma",
            "Edward",
            "Emily",
            "Ethan",
            "Eva",
            "Eric",
            # F
            "Frank",
            "Fred",
            "Forest",
            "Felicity",
            "Frances",
            # G
            "George",
            "Gary",
            "Gal",
            "Gerard",
            "Glenn",
            "Gwyneth",
            # H
            "Harrison",
            "Hugh",
            "Halle",
            "Helen",
            "Henry",
            "Harvey",
            # I
            "Ian",
            "Isaac",
            "Idris",
            "Isla",
            # J
            "Jack",
            "James",
            "Jennifer",
            "Jessica",
            "John",
            "Julia",
            "Johnny",
            # K
            "Kate",
            "Kevin",
            "Keanu",
            "Keira",
            "Kit",
            "Kristen",
            # L
            "Leonardo",
            "Liam",
            "Laura",
            "Lucy",
            "Luke",
            "Lupita",
            # M
            "Matt",
            "Michael",
            "Margot",
            "Morgan",
            "Mark",
            "Michelle",
            "Meryl",
            # N
            "Natalie",
            "Nicolas",
            "Nicole",
            "Naomi",
            "Neil",
            # O
            "Oscar",
            "Owen",
            "Olivia",
            "Orlando",
            # P
            "Paul",
            "Peter",
            "Patrick",
            "Penelope",
            "Pierce",
            # Q
            "Quentin",
            "Queen",
            # R
            "Robert",
            "Ryan",
            "Rachel",
            "Russell",
            "Reese",
            "Robin",
            # S
            "Samuel",
            "Scarlett",
            "Sebastian",
            "Sandra",
            "Steve",
            "Sophie",
            # T
            "Tom",
            "Timothée",
            "Tilda",
            "Timothy",
            "Tessa",
            # U
            "Uma",
            "Usher",
            # V
            "Vin",
            "Viggo",
            "Viola",
            "Vanessa",
            # W
            "Will",
            "Willem",
            "Woody",
            "Wesley",
            "Winona",
            # X
            "Xavier",
            # Y
            "Yalitza",
            # Z
            "Zendaya",
            "Zoe",
            "Zachary",
        ]

        print("🎬 ROZPOCZYNAM IMPORT AKTORÓW Z TMDb (SEARCH BY NAME)")
        print(f"📊 Cel: {len(search_queries)} queries × {max_pages_per_letter} stron")
        print("=" * 80)

        total_actors_all = 0
        total_queries = len(search_queries)

        try:
            for query_idx, query in enumerate(search_queries):
                print(f"\n{'='*80}")
                print(f"🔍 QUERY {query_idx + 1}/{total_queries}: '{query}'")
                print(f"{'='*80}")

                actors_this_query = 0

                for page in range(1, max_pages_per_letter + 1):
                    actors_to_add = []

                    try:
                        data = search_actors_by_letter(query, page)
                        results = data.get("results", [])
                        total_pages = data.get("total_pages", 0)

                        if page > total_pages or not results:
                            if page == 1:
                                print(
                                    f"   📄 1/{max_pages_per_letter} - Brak wyników (KONIEC)"
                                )
                            break

                        for person in results:
                            known_for = person.get("known_for_department")
                            if known_for != "Acting":
                                continue

                            actor_id = person["id"]
                            actor_name = person.get("name", "")

                            if not actor_name:
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

                            # Must have photo
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

                        # Save per page
                        if actors_to_add:
                            try:
                                db.session.add_all(actors_to_add)
                                db.session.commit()
                                actors_this_query += len(actors_to_add)
                                total_actors_all += len(actors_to_add)
                                print(
                                    f"   📄 {page}/{max_pages_per_letter} - Dodano {len(actors_to_add)} aktorów ✅"
                                )
                            except Exception as e:
                                db.session.rollback()
                                print(
                                    f"   📄 {page}/{max_pages_per_letter} - Błąd zapisu: {e} ❌"
                                )
                        else:
                            if page <= 3:  # Show first 3 pages
                                print(
                                    f"   📄 {page}/{max_pages_per_letter} - Brak nowych aktorów (skip)"
                                )

                        time.sleep(0.3)

                    except requests.RequestException as e:
                        print(f"   📄 {page}/{max_pages_per_letter} - Błąd HTTP: {e} ⚠️")
                        time.sleep(5)
                        continue

                    except Exception as e:
                        print(f"   📄 {page}/{max_pages_per_letter} - Błąd: {e} ⚠️")
                        continue

                print(
                    f"✅ Query '{query}' zakończone: {actors_this_query} aktorów (TOTAL: {total_actors_all})"
                )

        except KeyboardInterrupt:
            print("\n\n⚠️  PRZERWANO (Ctrl+C)")
            print(f"📊 TOTAL zapisanych aktorów: {total_actors_all}")

        print(f"\n{'='*80}")
        print(f"🎉 IMPORT ZAKOŃCZONY!")
        print(f"{'='*80}")
        print(f"📊 TOTAL aktorów dodanych: {total_actors_all}")
