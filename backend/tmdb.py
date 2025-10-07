import requests
import time

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"


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


with open("insert_actors.sql", mode="w", encoding="utf-8") as file:
    actors_fetched = 0
    max_actors = 100
    current_page = 1
    max_pages = 10  
    file.write(
        "INSERT INTO actors (actor_name, birth_date, birth_place, biography, photo_url, gender) VALUES\n"
    )

    insert_values = []

    while actors_fetched < max_actors and current_page <= max_pages:
        data = get_popular_actors(current_page)
        results = data.get("results", [])

        for actor in results:
            if actors_fetched >= max_actors:
                break

            actor_id = actor["id"]
            details = get_actor_details(actor_id)

          
            if not details.get("birthday") and not details.get("biography"):
                
                continue

            actor_name = sanitize(details.get("name"))
            birth_date = details.get("birthday")
            birth_date_sql = "NULL" if not birth_date else f"'{birth_date}'"
            birth_place = sanitize(details.get("place_of_birth"))
            biography = sanitize(details.get("biography"))
            profile_path = details.get("profile_path")
            photo_url = (
                f"https://image.tmdb.org/t/p/w500{profile_path}" if profile_path else ""
            )
            gender_code = details.get("gender", 0)
            gender = "K" if gender_code == 1 else "M" if gender_code == 2 else ""

            value = f"('{actor_name}', {birth_date_sql}, '{birth_place}', '{biography}', '{photo_url}', '{gender}')"
            insert_values.append(value)

            actors_fetched += 1
            print(f"Pobrano aktora: {actor_name} ({actors_fetched}/{max_actors})")

            time.sleep(0.25)  

        current_page += 1

    file.write(",\n".join(insert_values) + ";\n")

print(
    f"Plik insert_actors.sql został utworzony z {actors_fetched} aktorami, którzy mają datę urodzenia lub biografię."
)
