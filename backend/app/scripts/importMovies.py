import time
import requests
import sys
import os
import logging
from datetime import datetime

# Disable DEBUG logs
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
backend_dir = os.path.dirname(app_dir)
sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.movie_genre import MovieGenre

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"

# Genre mapping (TMDB ID -> DB ID)
TMDB_TO_DB_GENRES = {
    28: 64,  # Action -> Akcja
    12: 66,  # Adventure -> Przygodowy
    16: 52,  # Animation -> Animacja
    35: 28,  # Comedy -> Komedia
    80: 53,  # Crime -> Kryminał
    99: 12,  # Documentary -> Dokumentalny
    18: 63,  # Drama -> Dramat
    10751: 20,  # Family -> Familijny
    14: 67,  # Fantasy -> Fantasy
    36: 70,  # History -> Historyczny
    27: 26,  # Horror -> Horror
    10402: 68,  # Music -> Muzyczny
    9648: 55,  # Mystery -> Tajemnica
    10749: 56,  # Romance -> Romans
    878: 65,  # Science Fiction -> Sci-Fi
    10770: 12,  # TV Movie -> Dokumentalny
    53: 61,  # Thriller -> Thriller
    10752: 58,  # War -> Wojenny
    37: 59,  # Western -> Western
}


def discover_movies_by_year(year, page):
    """Discover movies by release year"""
    url = f"{base_url}/discover/movie"
    params = {
        "api_key": api_key,
        "language": language,
        "page": page,
        "primary_release_year": year,
        "sort_by": "popularity.desc",
        "include_adult": False,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_movie_details(movie_id):
    """Get full movie details"""
    url = f"{base_url}/movie/{movie_id}"
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
        pages_per_year = 5  # 100 filmów = 5 stron (20 per page)
        start_year = 2000
        end_year = datetime.now().year  # Current year (2025)

        years = list(range(start_year, end_year + 1))  # [2000, 2001, ..., 2025]

        print("🎬 ROZPOCZYNAM IMPORT FILMÓW Z TMDb (BY YEAR)")
        print(
            f"📊 Cel: {len(years)} lat ({start_year}-{end_year}) × {pages_per_year} stron (100 filmów/rok)"
        )
        print("=" * 80)

        total_movies_all = 0
        total_years = len(years)

        try:
            for year_idx, target_year in enumerate(years):
                print(f"\n{'='*80}")
                print(f"📅 ROK {year_idx + 1}/{total_years}: {target_year}")
                print(f"{'='*80}")

                movies_this_year = 0

                for page in range(1, pages_per_year + 1):
                    movies_to_add = []  # Buffer dla current page

                    try:
                        data = discover_movies_by_year(target_year, page)
                        results = data.get("results", [])

                        if not results:
                            print(
                                f"   📄 {page}/{pages_per_year} - Brak wyników (KONIEC)"
                            )
                            break

                        for movie_data in results:
                            movie_id = movie_data.get("id")
                            title = movie_data.get("title")

                            # Check duplicate
                            existing_movie = Movie.query.filter_by(title=title).first()
                            if existing_movie:
                                continue

                            # Get full details
                            try:
                                details = get_movie_details(movie_id)
                            except Exception:
                                continue

                            release_date = details.get("release_date")
                            description = details.get("overview")
                            poster_path = details.get("poster_path")
                            poster_url = (
                                f"https://image.tmdb.org/t/p/w500{poster_path}"
                                if poster_path
                                else ""
                            )
                            duration = details.get("runtime")

                            # Get production country (first)
                            production_countries = details.get(
                                "production_countries", []
                            )
                            country = (
                                production_countries[0]["name"]
                                if production_countries
                                else ""
                            )

                            original_language = details.get("original_language", "")

                            # Get trailer (first YouTube trailer)
                            trailer_url = ""
                            try:
                                videos_url = f"{base_url}/movie/{movie_id}/videos"
                                videos_resp = requests.get(
                                    videos_url, params={"api_key": api_key}, timeout=10
                                )
                                videos_data = videos_resp.json()
                                videos = videos_data.get("results", [])
                                for video in videos:
                                    if (
                                        video.get("site") == "YouTube"
                                        and video.get("type") == "Trailer"
                                    ):
                                        trailer_url = f"https://www.youtube.com/watch?v={video.get('key')}"
                                        break
                            except Exception:
                                pass

                            # Skip incomplete
                            if not all([release_date, description, poster_url]):
                                continue

                            title = sanitize(title)
                            description = sanitize(description)

                            # Create Movie object
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

                            db.session.add(movie_obj)
                            db.session.flush()  # Get movie_id

                            # Add genres
                            genre_ids = details.get("genre_ids", []) or details.get(
                                "genres", []
                            )
                            if isinstance(genre_ids, list) and len(genre_ids) > 0:
                                # Handle both formats (discover returns IDs, details returns objects)
                                if isinstance(genre_ids[0], dict):
                                    genre_ids = [g["id"] for g in genre_ids]

                                for tmdb_genre_id in genre_ids:
                                    db_genre_id = TMDB_TO_DB_GENRES.get(tmdb_genre_id)
                                    if db_genre_id:
                                        # Check genre exists
                                        genre_exists = db.session.query(
                                            db.session.query(Genre)
                                            .filter_by(genre_id=db_genre_id)
                                            .exists()
                                        ).scalar()

                                        if genre_exists:
                                            relation = MovieGenre(
                                                movie_id=movie_obj.movie_id,
                                                genre_id=db_genre_id,
                                            )
                                            db.session.add(relation)

                            movies_to_add.append(title)  # Track for log

                            time.sleep(0.05)

                        # Save po każdej stronie
                        if movies_to_add:
                            try:
                                db.session.commit()
                                movies_this_year += len(movies_to_add)
                                total_movies_all += len(movies_to_add)
                                print(
                                    f"   📄 {page}/{pages_per_year} - Dodano {len(movies_to_add)} filmów ✅"
                                )
                            except Exception as e:
                                db.session.rollback()
                                print(
                                    f"   📄 {page}/{pages_per_year} - Błąd zapisu: {e} ❌"
                                )
                        else:
                            print(
                                f"   📄 {page}/{pages_per_year} - Brak nowych filmów (skip)"
                            )

                        time.sleep(0.3)  # Rate limit

                    except requests.RequestException as e:
                        print(f"   📄 {page}/{pages_per_year} - Błąd HTTP: {e} ⚠️")
                        db.session.rollback()
                        time.sleep(5)
                        continue

                    except Exception as e:
                        print(f"   📄 {page}/{pages_per_year} - Błąd: {e} ⚠️")
                        db.session.rollback()
                        continue

                print(
                    f"\n✅ Rok {target_year} zakończony: {movies_this_year} filmów (TOTAL: {total_movies_all})"
                )

        except KeyboardInterrupt:
            print("\n\n⚠️  PRZERWANO (Ctrl+C)")
            print(f"📊 TOTAL zapisanych filmów: {total_movies_all}")

        print(f"\n{'='*80}")
        print(f"🎉 IMPORT ZAKOŃCZONY!")
        print(f"{'='*80}")
        print(f"📊 TOTAL filmów dodanych: {total_movies_all}")
