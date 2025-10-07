import time
import requests
import sys
import os
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.movie import Movie  
import random

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"
spinner = ["-", "\\", "|", "/"]
BATCH_SIZE = 50
CHECKPOINT_FILE = "movie_import_checkpoint.txt"


def discover_movies(start_date, end_date, page=1):
    url = f"{base_url}/discover/movie"
    params = {
        "api_key": api_key,
        "language": language,
        "sort_by": "vote_count.desc",
        "primary_release_date.gte": start_date,
        "primary_release_date.lte": end_date,
        "page": page,
        "include_adult": False,
        "include_video": False,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_movie_details(movie_id):
    url = f"{base_url}/movie/{movie_id}"
    params = {"api_key": api_key, "language": language}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def sanitize(text):
    if text is None:
        return ""
    return text.replace("\n", " ").replace("\r", " ").strip()


def daterange(start_date, end_date, step_months=4):
    current = start_date
    while current <= end_date:
        next_date = current + timedelta(days=step_months * 30)  # approx 4 months
        if next_date > end_date:
            next_date = end_date
        yield current, next_date
        current = next_date + timedelta(days=1)


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            line = f.readline().strip()
            if line:
                parts = line.split("|")
                return parts[0], int(parts[1])
    return None, 1


def save_checkpoint(period_start, page):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(f"{period_start}|{page}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        total_added = 0
        step_months = 4
        start_year = 2000
        end_year = 2025
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)

        checkpoint_period_start, checkpoint_page = None, 1
        checkpoint_reached = True

        for period_start, period_end in daterange(start_date, end_date, step_months):
            start_str = period_start.strftime("%Y-%m-%d")
            end_str = period_end.strftime("%Y-%m-%d")

            page = 1 

            try:
                data = discover_movies(start_str, end_str, page)
                movies = data.get("results", [])[:10]  

                movies_to_commit = []

                for movie_summary in movies:
                    movie_id = movie_summary["id"]

                    existing_movie = Movie.query.filter_by(movie_id=movie_id).first()
                    if existing_movie:
                        continue

                    details = get_movie_details(movie_id)

                    title = details.get("title", "")
                    release_date = details.get("release_date")
                    description = sanitize(details.get("overview", ""))
                    poster_path = details.get("poster_path")
                    poster_url = (
                        f"https://image.tmdb.org/t/p/w500{poster_path}"
                        if poster_path
                        else None
                    )
                    duration = details.get("runtime")
                    origin_countries = details.get("origin_country") or []
                    country = origin_countries[0] if origin_countries else None
                    original_language = details.get("original_language")
                    trailer_url = None

                    required_fields = [
                        title,
                        release_date,
                        description,
                        poster_url,
                        duration,
                        country,
                        original_language,
                    ]

                    if any(
                        field is None
                        or (isinstance(field, str) and field.strip() == "")
                        or (isinstance(field, int) and field == 0)
                        for field in required_fields
                    ):
                        continue

                    exists_title = Movie.query.filter(
                        Movie.title == title, Movie.release_date == release_date
                    ).first()
                    if exists_title:
                        continue

                    movie_obj = Movie(
                        title=title,
                        release_date=release_date,
                        description=description,
                        poster_url=poster_url,
                        duration_minutes=duration,
                        country=country,
                        original_language=original_language,
                        trailer_url=trailer_url,
                    )

                    movies_to_commit.append(movie_obj)
                    total_added += 1

                if movies_to_commit:
                    db.session.add_all(movies_to_commit)
                    db.session.commit()

                print(
                    f"\nZakończono pobieranie i dodano {len(movies_to_commit)} filmów dla okresu {start_str} - {end_str}."
                )

                save_checkpoint(start_str, page)

                time.sleep(0.5)

            except Exception as e:
                print(
                    f"\nBłąd podczas pobierania filmów dla {start_str} - {end_str}: {str(e)}"
                )

        print(f"\nKoniec importu. Łącznie dodanych filmów: {total_added}")
