import requests
import os
from app import create_app
from app.extensions import db
from app.models.director import Director
from app.models.movie import Movie
from app.models.movie_director import MovieDirector

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
tmdb_search_url = "https://api.themoviedb.org/3/search/person"
tmdb_credits_url = "https://api.themoviedb.org/3/person/{person_id}/movie_credits"
CHECKPOINT_FILE = "director_movies_checkpoint.txt"


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                return line
    return None


def save_checkpoint(director_name):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(director_name)


app = create_app()
with app.app_context():
    last_director = load_checkpoint()
    checkpoint_reached = last_director is None  # start from beginning if no checkpoint

    directors = Director.query.order_by(Director.director_id).all()
    total_directors = len(directors)

    for idx, director in enumerate(directors, start=1):
        if not checkpoint_reached:
            if director.director_name == last_director:
                checkpoint_reached = True
            else:
                continue  # skip until checkpoint reached

        print(
            f"Przetwarzam reżysera {idx} z {total_directors}: {director.director_name}"
        )

        # Step 1: search TMDb person by director name
        search_params = {
            "api_key": api_key,
            "language": "pl-PL",
            "query": director.director_name,
            "include_adult": False,
        }
        search_resp = requests.get(tmdb_search_url, params=search_params).json()
        results = search_resp.get("results", [])
        if not results:
            print(f"Nie znaleziono reżysera TMDb: {director.director_name}")
            save_checkpoint(director.director_name)
            continue

        tmdb_person_id = results[0]["id"]

        # Step 2: get person movie credits from TMDb
        credits_params = {"api_key": api_key, "language": "pl-PL"}
        credits_resp = requests.get(
            tmdb_credits_url.format(person_id=tmdb_person_id), params=credits_params
        ).json()

        saved_movies = 0
        movies_credits = credits_resp.get(
            "crew", []
        )  # director films usually appear in crew
        # Filter only directing jobs
        directing_credits = [m for m in movies_credits if m.get("job") == "Director"]

        for film in directing_credits:
            title = film.get("title")
            tmdb_movie_id = film.get("id")

            # Search movie in your database by title
            movie = Movie.query.filter_by(title=title).first()
            if not movie:
                continue

            # Check if director-movie relation already exists
            exists = MovieDirector.query.filter_by(
                director_id=director.director_id, movie_id=movie.movie_id
            ).first()
            if exists:
                continue

            # Add new director-movie relation
            rel = MovieDirector(
                director_id=director.director_id, movie_id=movie.movie_id
            )
            db.session.add(rel)
            saved_movies += 1

        db.session.commit()
        print(f"Reżyser {director.director_name} dodał {saved_movies} filmów.")

        save_checkpoint(director.director_name)
