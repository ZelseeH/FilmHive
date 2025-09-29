import requests
import os
from app import create_app
from app.extensions import db
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.movie_genre import MovieGenre  # model many-to-many

API_KEY = "d729e3223cb49b1d62ae3feb6a2cd2b7"
SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie/{movie_id}"
CHECKPOINT_FILE = "movie_genres_checkpoint5.txt"


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                return line
    return None


def save_checkpoint(movie_title):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(movie_title)


app = create_app()
with app.app_context():
    last_movie = load_checkpoint()
    checkpoint_reached = last_movie is None

    movies = Movie.query.order_by(Movie.movie_id).all()
    total_movies = len(movies)

    for idx, movie in enumerate(movies, start=1):
        if not checkpoint_reached:
            if movie.title == last_movie:
                checkpoint_reached = True
            else:
                continue

        print(f"Przetwarzam film {idx} z {total_movies}: {movie.title}")

        params = {
            "api_key": API_KEY,
            "language": "pl-PL",
            "query": movie.title,
            "include_adult": False,
        }
        resp = requests.get(SEARCH_MOVIE_URL, params=params)
        resp.raise_for_status()
        search_results = resp.json().get("results", [])

        if not search_results:
            print(f"Nie znaleziono filmu TMDb: {movie.title}")
            save_checkpoint(movie.title)
            continue

        tmdb_movie_id = search_results[0]["id"]

        details_resp = requests.get(
            MOVIE_DETAILS_URL.format(movie_id=tmdb_movie_id),
            params={"api_key": API_KEY, "language": "pl-PL"},
        )
        details_resp.raise_for_status()
        details = details_resp.json()

        genres = details.get("genres", [])
        if not genres:
            print(f"Brak gatunków dla filmu: {movie.title}")
            save_checkpoint(movie.title)
            continue

        added_genres_count = 0
        for genre_data in genres:
            genre_name = genre_data.get("name")
            if not genre_name:
                continue

            genre = Genre.query.filter_by(genre_name=genre_name).first()
            if not genre:
                print(f"Nie znaleziono gatunku w bazie: {genre_name} (pomijam)")
                continue

            assoc = (
                db.session.query(MovieGenre)
                .filter(
                    MovieGenre.movie_id == movie.movie_id,
                    MovieGenre.genre_id == genre.genre_id,
                )
                .first()
            )

            if assoc:
                continue

            new_assoc = MovieGenre(movie_id=movie.movie_id, genre_id=genre.genre_id)
            db.session.add(new_assoc)
            added_genres_count += 1

        db.session.commit()

        print(f"Dodano {added_genres_count} gatunków do filmu '{movie.title}'")

        save_checkpoint(movie.title)
