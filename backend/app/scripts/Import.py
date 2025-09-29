import requests
import os
from app import create_app
from app.extensions import db
from app.models.actor import Actor
from app.models.movie import Movie
from app.models.movie_actor import MovieActor
import time
import sys

API_KEY = "d729e3223cb49b1d62ae3feb6a2cd2b7"
TMDB_SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_CREDITS_URL = "https://api.themoviedb.org/3/movie/{movie_id}/credits"
TMDB_PERSON_URL = "https://api.themoviedb.org/3/person/{person_id}"
LANGUAGE = "pl-PL"
CHECKPOINT_FILE = "movie_actor_checkpoint.txt"

spinner = ["-", "\\", "|", "/"]


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                print(f"Resuming from checkpoint at film '{line}'")
                return line
    return None


def save_checkpoint(title):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(title)
    print(f"Checkpoint saved at film '{title}'")


def sanitize(text):
    if not text:
        return ""
    return text.replace("\n", " ").replace("\r", " ").replace("'", "''").strip()


def get_actor_details(actor_id):
    url = TMDB_PERSON_URL.format(person_id=actor_id)
    params = {"api_key": API_KEY, "language": LANGUAGE}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def main():
    app = create_app()
    with app.app_context():
        movie_titles = [m.title for m in Movie.query.order_by(Movie.movie_id).all()]
        total_movies = len(movie_titles)
        print(f"Found {total_movies} movies to process.")

        last_processed = load_checkpoint()
        checkpoint_reached = last_processed is None

        for idx, title in enumerate(movie_titles, start=1):
            if not checkpoint_reached:
                if title == last_processed:
                    checkpoint_reached = True
                    print(f"Checkpoint reached at '{title}', resuming...")
                else:
                    continue

            print(f"\nProcessing movie {idx}/{total_movies}: '{title}'")

            try:
                # Search movie in TMDb
                params = {
                    "api_key": API_KEY,
                    "language": LANGUAGE,
                    "query": title,
                    "include_adult": False,
                    "page": 1,
                }
                search_resp = requests.get(TMDB_SEARCH_MOVIE_URL, params=params)
                search_resp.raise_for_status()
                search_data = search_resp.json()
                results = search_data.get("results", [])
                if not results:
                    print(f"Movie '{title}' not found on TMDb.")
                    save_checkpoint(title)
                    continue

                tmdb_movie_id = results[0]["id"]

                movie_obj = Movie.query.filter_by(title=title).first()
                if not movie_obj:
                    print(f"Local movie '{title}' not found, skipping.")
                    save_checkpoint(title)
                    continue

                # Get credits from TMDb
                credits_resp = requests.get(
                    TMDB_MOVIE_CREDITS_URL.format(movie_id=tmdb_movie_id),
                    params={"api_key": API_KEY, "language": LANGUAGE},
                )
                credits_resp.raise_for_status()
                credits_json = credits_resp.json()
                cast = credits_json.get("cast", [])[:5]

                added_actors = 0
                added_roles = 0
                spin_idx = 0

                for actor_data in cast:
                    actor_name = actor_data.get("name")
                    character = actor_data.get("character", "")

                    # Check actor existence by name
                    actor = Actor.query.filter_by(actor_name=actor_name).first()

                    if not actor:
                        try:
                            details = get_actor_details(actor_data.get("id"))
                            # Extract details
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

                            missing_fields = []
                            if not birth_date:
                                missing_fields.append("birth_date")
                            if not birth_place:
                                missing_fields.append("birth_place")
                            if not biography:
                                missing_fields.append("biography")
                            if not photo_url:
                                missing_fields.append("photo_url")
                            if not gender:
                                missing_fields.append("gender")

                            if missing_fields:
                                print(
                                    f"Skipping actor '{actor_name}' due to missing fields: {', '.join(missing_fields)}."
                                )
                                continue

                            actor_name_s = sanitize(actor_name)
                            birth_place_s = sanitize(birth_place)
                            biography_s = sanitize(biography)

                            actor = Actor(
                                actor_name=actor_name_s,
                                birth_date=birth_date,
                                birth_place=birth_place_s,
                                biography=biography_s,
                                photo_url=photo_url,
                                gender=gender,
                            )

                            db.session.add(actor)
                            db.session.flush()
                            added_actors += 1

                        except requests.RequestException as e:
                            print(
                                f"Failed to fetch details for actor '{actor_name}': {e}"
                            )
                            continue

                    # Check if relation exists
                    relation = MovieActor.query.filter_by(
                        movie_id=movie_obj.movie_id, actor_id=actor.actor_id
                    ).first()
                    if relation:
                        continue

                    rel = MovieActor(
                        movie_id=movie_obj.movie_id,
                        actor_id=actor.actor_id,
                        movie_role=character,
                    )
                    db.session.add(rel)
                    added_roles += 1

                    sys.stdout.write(
                        f"\rProcessing actors... {spinner[spin_idx % len(spinner)]}"
                    )
                    sys.stdout.flush()
                    spin_idx += 1
                    time.sleep(0.05)

                db.session.commit()
                print(
                    f"\nFor '{title}': added {added_actors} new actors and {added_roles} roles."
                )
                save_checkpoint(title)

            except requests.RequestException as e:
                print(f"HTTP error on movie '{title}': {e}")
                save_checkpoint(title)
            except Exception as e:
                print(f"Unexpected error processing '{title}': {e}")
                db.session.rollback()
                save_checkpoint(title)


if __name__ == "__main__":
    main()
