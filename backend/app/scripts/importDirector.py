import time
import requests
import sys
from app import create_app
from app.extensions import db
from app.models.director import Director

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"
spinner = ["-", "\\", "|", "/"]

directors_list = [
    "Joseph Kosinski",
    "David Ayer",
    "Patty Jenkins",
    "James Wan",
    "Shawn Levy",
    "David Fincher",
    "J.J. Abrams",
    "Denis Villeneuve",
    "Michael Mann",
    "John Favreau",
    "Fede Álvarez",
    "Taika Waititi",
    "Zack Snyder",
    "Rian Johnson",
    "Adam Wingard",
    "Robert Eggers",
    "Todd Phillips",
    "Christopher McQuarrie",
    "Marc Webb",
    "Guy Ritchie",
    "Duncan Jones",
    "Joe Wright",
    "Shane Black",
    "Paul Greengrass",
    "Gareth Edwards",
    "Edgar Wright",
    "Neil Marshall",
    "M. Night Shyamalan",
    "Rob Cohen",
    "Brian De Palma",
    "Robert Zemeckis",
    "Peter Jackson",
    "George Miller",
    "Ang Lee",
    "Darren Aronofsky",
    "Tim Miller",
    "Neil Burger",
    "Roland Emmerich",
    "Ron Clements",
    "John Musker",
    "Brad Bird",
    "Henry Selick",
    "Pete Docter",
    "Andrew Stanton",
    "Rich Moore",
    "Byron Howard",
    "Jared Hess",
    "Lena Dunham",
    "Sofia Coppola",
    "Kelly Reichardt",
    "Greta Gerwig",
    "Mira Nair",
    "Lynne Ramsay",
    "Andrea Arnold",
    "Debra Granik",
    "Céline Sciamma",
    "Jane Campion",
    "Hirokazu Kore-eda",
    "Bong Joon-ho",
    "Park Chan-wook",
    "Apichatpong Weerasethakul",
    "Alejandro González Iñárritu",
    "Alfonso Cuarón",
    "Guillermo del Toro",
    "Spike Jonze",
    "Wes Anderson",
    "Noah Baumbach",
    "Richard Linklater",
    "Paul Thomas Anderson",
    "Jim Jarmusch",
    "Sofia Coppola",
    "David Lynch",
    "Lars von Trier",
    "Harmony Korine",
    "Gaspar Noé",
    "Michael Haneke",
    "Kathryn Bigelow",
    "Patty Jenkins",
    "Ava DuVernay",
    "Gina Prince-Bythewood",
    "Niki Caro",
    "Marielle Heller",
    "Debra Granik",
    "Andrea Arnold",
    "Claire Denis",
    "Agnès Varda",
    "Jane Campion",
    "Lucrecia Martel",
    "Kelly Reichardt",
    "Debra Granik",
    "Jennifer Kent",
    "Céline Sciamma",
    "Ana Lily Amirpour",
    "Ana Lily Amirpour",
    "Alice Rohrwacher",
    "Nadine Labaki",
    "Chloé Zhao",
    "Lulu Wang",
]


def search_person(query, page=1):
    url = f"{base_url}/search/person"
    params = {
        "api_key": api_key,
        "language": language,
        "query": query,
        "page": page,
        "include_adult": False,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_person_details(person_id):
    url = f"{base_url}/person/{person_id}"
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
        directors_to_add = []
        spin_idx = 0
        total_added = 0

        for director_name in directors_list:
            try:
                # Szukaj osoby według nazwy
                search_data = search_person(director_name)
                results = search_data.get("results", [])

                # Szukamy reżysera lub scenarzysty w wynikach (Directing lub Writing)
                director_found = None
                for person in results:
                    if person.get("known_for_department") in ["Directing", "Writing"]:
                        director_found = person
                        break

                if not director_found:
                    print(f"\nBrak reżysera '{director_name}' w wynikach wyszukiwania.")
                    continue

                person_id = director_found["id"]

                # Sprawdź, czy już jest w bazie
                exists = Director.query.filter_by(director_name=director_name).first()
                if exists:
                    print(f"\nReżyser '{director_name}' już jest w bazie.")
                    continue

                details = get_person_details(person_id)

                birth_date = details.get("birthday")
                birth_place = details.get("place_of_birth")
                biography = details.get("biography") or ""  # Biografia może być pusta
                profile_path = details.get("profile_path")
                photo_url = (
                    f"https://image.tmdb.org/t/p/w500{profile_path}"
                    if profile_path
                    else ""
                )
                gender_code = details.get("gender", 0)
                gender = "K" if gender_code == 1 else "M" if gender_code == 2 else ""

                # Sprawdzamy brakujące pola oprócz biografii i wypisujemy które
                required_fields = {
                    "birth_date": birth_date,
                    "birth_place": birth_place,
                    "photo_url": photo_url,
                    "gender": gender,
                }

                missing_fields = [
                    field for field, value in required_fields.items() if not value
                ]

                if missing_fields:
                    print(
                        f"\nPominięto reżysera '{director_name}' ze względu na brak danych: {', '.join(missing_fields)}."
                    )
                    continue

                sanitized_name = sanitize(director_name)
                birth_place = sanitize(birth_place)
                biography = sanitize(biography)

                if any(d.director_name == sanitized_name for d in directors_to_add):
                    print(f"\nReżyser '{director_name}' już jest na liście do dodania.")
                    continue
                director_obj = Director(
                    director_name=sanitized_name,
                    birth_date=birth_date,
                    birth_place=birth_place,
                    biography=biography,
                    photo_url=photo_url,
                    gender=gender,
                )

                directors_to_add.append(director_obj)
                total_added += 1

                sys.stdout.write(
                    f"\rDodano reżyserów: {total_added} {spinner[spin_idx % len(spinner)]}"
                )
                sys.stdout.flush()
                spin_idx += 1

                time.sleep(0.05)  # Łagodzenie zapytań do API

            except Exception as e:
                print(f"\nBłąd podczas przetwarzania '{director_name}': {str(e)}")

        print("\nZapisywanie do bazy...")

        if directors_to_add:
            try:
                db.session.add_all(directors_to_add)
                db.session.commit()
                print(f"Dodano {len(directors_to_add)} reżyserów do bazy.")
            except Exception as e:
                db.session.rollback()
                print(f"Błąd przy zapisywaniu do bazy: {str(e)}")
        else:
            print("Brak reżyserów do dodania.")
