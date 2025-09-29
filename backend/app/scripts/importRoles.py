import requests
import os
from app import create_app
from app.extensions import db
from app.models.actor import Actor
from app.models.movie import Movie
from app.models.movie_actor import MovieActor

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
tmdb_search_url = "https://api.themoviedb.org/3/search/person"
tmdb_credits_url = "https://api.themoviedb.org/3/person/{person_id}/movie_credits"
CHECKPOINT_FILE = "actor_roles_checkpoint.txt"


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                return line
    return None


def save_checkpoint(actor_name):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(actor_name)


app = create_app()
with app.app_context():
    last_actor = load_checkpoint()
    checkpoint_reached = last_actor is None  # jeśli brak checkpointa, start od początku

    actors = Actor.query.order_by(Actor.actor_id).all()
    total_actors = len(actors)

    for idx, actor in enumerate(actors, start=1):
        if not checkpoint_reached:
            if actor.actor_name == last_actor:
                checkpoint_reached = True
            else:
                continue  # pomiń aktorów do checkpointa

        print(f"Przetwarzam aktora {idx} z {total_actors}: {actor.actor_name}")

        search_params = {
            "api_key": api_key,
            "language": "pl-PL",
            "query": actor.actor_name,
            "include_adult": False,
        }
        search_resp = requests.get(tmdb_search_url, params=search_params).json()
        results = search_resp.get("results", [])
        if not results:
            print(f"Nie znaleziono aktora TMDb: {actor.actor_name}")
            save_checkpoint(actor.actor_name)
            continue

        tmdb_person_id = results[0]["id"]

        credits_params = {"api_key": api_key, "language": "pl-PL"}
        credits_resp = requests.get(
            tmdb_credits_url.format(person_id=tmdb_person_id), params=credits_params
        ).json()

        saved_roles = 0
        for film in credits_resp.get("cast", []):
            title = film.get("title")
            character = film.get("character", "")
            movie = Movie.query.filter_by(title=title).first()
            if not movie:
                continue

            exists = MovieActor.query.filter_by(
                movie_id=movie.movie_id, actor_id=actor.actor_id
            ).first()
            if exists:
                continue

            rel = MovieActor(
                movie_id=movie.movie_id, actor_id=actor.actor_id, movie_role=character
            )
            db.session.add(rel)
            saved_roles += 1
        db.session.commit()
        print(f"Zapisano {saved_roles} filmów dla aktora {actor.actor_name}.")

        save_checkpoint(actor.actor_name)
