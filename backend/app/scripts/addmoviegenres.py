import requests
import os
import time
import sys
import logging

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

API_KEY = "d729e3223cb49b1d62ae3feb6a2cd2b7"
SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie/{movie_id}"
CHECKPOINT_FILE = "movie_genres_checkpoint_repair.txt"

# POPRAWIONE mapping
TMDB_TO_DB_GENRES = {
    # English TMDb genres
    "Action": 64,
    "Adventure": 66,
    "Animation": 52,
    "Comedy": 28,
    "Crime": 53,
    "Documentary": 12,
    "Drama": 63,
    "Family": 20,
    "Fantasy": 67,
    "History": 70,
    "Horror": 26,
    "Music": 68,
    "Mystery": 55,
    "Romance": 56,
    "Science Fiction": 65,
    "TV Movie": 12,
    "Thriller": 61,
    "War": 58,
    "Western": 59,
    # Polish genres
    "Akcja": 64,
    "Przygodowy": 66,
    "Przygoda": 66,
    "Animacja": 52,
    "Komedia": 28,
    "Kryminał": 53,
    "Kryminalne": 53,
    "Kryminalna": 53,
    "Dokumentalny": 12,
    "Dokumentalizowany": 11,
    "Dramat": 63,
    "Dramat obyczajowy": 15,
    "Dramat sądowy": 16,
    "Familijny": 20,
    "Dla całej rodziny": 20,
    "Fantasy": 67,
    "Fantastyczny": 67,
    "Historyczny": 70,
    "Historia": 70,
    "Horror": 26,
    "Muzyczny": 68,
    "Muzyka": 68,
    "Tajemnica": 55,
    "Romans": 56,
    "Romantyczny": 56,
    "Sci-Fi": 65,
    "Science Fiction": 65,
    "Film telewizyjny": 12,
    "Dreszczowiec": 17,
    "Thriller": 61,
    "Wojenny": 58,
    "Wojna": 58,
    "Western": 59,
    # Specjalistyczne
    "Biograficzny": 7,
    "Biography": 7,
    "Biografia": 7,
    "Młodzieżowy": 10,
    "Dla młodzieży": 10,
    "Teen": 10,
    "Anime": 4,
    "Erotyczny": 18,
    "Erotic": 18,
    "Gangsterski": 23,
    "Gangster": 23,
    "Film-Noir": 22,
    "Noir": 22,
    "Neo-noir": 89,
    "Katastroficzny": 27,
    "Disaster": 27,
    "Baśń": 5,
    "Fairy Tale": 5,
    "Sportowy": 69,
    "Sports": 69,
    "Psychologiczny": 71,
    "Psychological": 71,
    "Czarna komedia": 72,
    "Black Comedy": 72,
    "Supernatural": 73,
    "Nadprzyrodzony": 73,
    "Mockumentary": 74,
    "Dystopian": 75,
    "Dystopia": 75,
    "Shonen": 76,
    "Seinen": 77,
    "Shoujo": 78,
    "Slice of Life": 79,
    "Wycinek życia": 79,
    "Suspense": 80,
    "Napięcie": 80,
    "Polityczny": 81,
    "Political": 81,
    "Religijny": 82,
    "Religious": 82,
    "Satyryczny": 83,
    "Satire": 83,
    "Heist": 84,
    "Napad": 84,
    "Zombie": 85,
    "Steampunk": 86,
    "Cyberpunk": 87,
    "Space Opera": 88,
    "Opera kosmiczna": 88,
    "Thriller prawniczy": 90,
    "Legal Thriller": 90,
    "Szpiegowski": 91,
    "Spy": 91,
    "Komedia kryminalna": 29,
    "Komedia romantyczna": 31,
    "Komedia rom.": 31,
    "Groteska filmowa": 24,
}


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                lines = content.split("\n")
                last_title = lines[0]
                last_index = int(lines[1]) if len(lines) > 1 else 0
                print(
                    f"🔄 Checkpoint: resuming from '{last_title}' (#{last_index + 1})"
                )
                return last_title, last_index
    return None, 0


def save_checkpoint(title, index):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{index}")


def get_all_movies():
    """Get ALL movies (nie tylko bez gatunków)"""
    return db.session.query(Movie).order_by(Movie.movie_id).all()


def search_movie_in_tmdb(movie_title, movie_year=None):
    params = {
        "api_key": API_KEY,
        "language": "pl-PL",
        "query": movie_title,
        "include_adult": False,
        "page": 1,
    }

    if movie_year:
        params["year"] = movie_year

    try:
        resp = requests.get(SEARCH_MOVIE_URL, params=params, timeout=10)
        resp.raise_for_status()
        search_results = resp.json().get("results", [])

        if search_results:
            best_match = search_results[0]
            if movie_year:
                for result in search_results:
                    release_date = result.get("release_date", "")
                    if release_date and str(movie_year) in release_date:
                        best_match = result
                        break
            return best_match["id"]
        else:
            return None

    except Exception as e:
        print(f"     ⚠️  Błąd TMDb search: {str(e)}")
        return None


def get_movie_genres_from_tmdb(tmdb_movie_id):
    try:
        details_resp = requests.get(
            MOVIE_DETAILS_URL.format(movie_id=tmdb_movie_id),
            params={"api_key": API_KEY, "language": "pl-PL"},
            timeout=10,
        )
        details_resp.raise_for_status()
        details = details_resp.json()
        return details.get("genres", [])

    except Exception as e:
        print(f"     ⚠️  Błąd TMDb details: {str(e)}")
        return []


def map_tmdb_genre_to_db(tmdb_genre_name):
    """Map TMDb genre name to DB genre_id"""
    if tmdb_genre_name in TMDB_TO_DB_GENRES:
        return TMDB_TO_DB_GENRES[tmdb_genre_name]

    genre_lower = tmdb_genre_name.lower()
    for tmdb_name, db_id in TMDB_TO_DB_GENRES.items():
        if genre_lower in tmdb_name.lower() or tmdb_name.lower() in genre_lower:
            return db_id

    return None


def main():
    app = create_app()

    with app.app_context():
        print("🎬 NAPRAWA GATUNKÓW - SPRAWDZAM WSZYSTKIE FILMY")
        print("(Dodaję brakujące gatunki, nie usuwam istniejących)")
        print("=" * 80)

        print("📊 Pobieram listę wszystkich filmów...")
        all_movies = get_all_movies()
        total_movies = len(all_movies)

        print(f"📊 ZNALEZIONO {total_movies} FILMÓW DO SPRAWDZENIA")
        print("=" * 80)

        last_title, start_index = load_checkpoint()

        total_added_relations = 0
        total_skipped = 0
        total_errors = 0
        total_no_genres = 0
        total_already_complete = 0

        try:
            for i in range(start_index, total_movies):
                movie = all_movies[i]
                current_number = i + 1

                print(f"\n🎭 FILM {current_number}/{total_movies}: '{movie.title}'")
                print(f"📈 POSTĘP: {(current_number/total_movies*100):.1f}%")

                try:
                    # Check current genres
                    existing_genres = MovieGenre.query.filter_by(
                        movie_id=movie.movie_id
                    ).all()
                    existing_genre_ids = {mg.genre_id for mg in existing_genres}

                    print(f"   📋 Obecne gatunki: {len(existing_genre_ids)}")

                    # Get TMDb genres
                    movie_year = None
                    if hasattr(movie, "release_date") and movie.release_date:
                        movie_year = movie.release_date.year

                    print(f"   🔍 Szukam w TMDb...")
                    tmdb_movie_id = search_movie_in_tmdb(movie.title, movie_year)

                    if not tmdb_movie_id:
                        print(f"   ❌ Nie znaleziono w TMDb")
                        total_no_genres += 1
                        save_checkpoint(movie.title, i)
                        continue

                    print(f"   ✅ TMDb ID: {tmdb_movie_id}")

                    tmdb_genres = get_movie_genres_from_tmdb(tmdb_movie_id)

                    if not tmdb_genres:
                        print(f"   ❌ Brak gatunków w TMDb")
                        total_no_genres += 1
                        save_checkpoint(movie.title, i)
                        continue

                    print(f"   🎭 TMDb gatunki: {[g['name'] for g in tmdb_genres]}")

                    # Add missing genres (NIE usuwaj existing!)
                    relations_added = 0
                    mapped_genres = []

                    for genre_data in tmdb_genres:
                        tmdb_genre_name = genre_data.get("name")
                        if not tmdb_genre_name:
                            continue

                        db_genre_id = map_tmdb_genre_to_db(tmdb_genre_name)

                        if not db_genre_id:
                            print(f"   ⚠️  Nie zmapowano: {tmdb_genre_name}")
                            continue

                        # Skip jeśli już istnieje
                        if db_genre_id in existing_genre_ids:
                            continue

                        # Check genre exists in DB
                        genre_exists = db.session.query(
                            db.session.query(Genre)
                            .filter_by(genre_id=db_genre_id)
                            .exists()
                        ).scalar()

                        if not genre_exists:
                            print(f"   ⚠️  Genre ID {db_genre_id} nie istnieje w bazie")
                            continue

                        # Add missing relation
                        relation = MovieGenre(
                            movie_id=movie.movie_id, genre_id=db_genre_id
                        )
                        db.session.add(relation)
                        relations_added += 1
                        mapped_genres.append(f"{tmdb_genre_name} -> {db_genre_id}")

                    if relations_added > 0:
                        db.session.commit()
                        total_added_relations += relations_added
                        print(f"   💾 Dodano {relations_added} brakujących gatunków:")
                        for mapped in mapped_genres:
                            print(f"     ✅ {mapped}")
                    else:
                        print(f"   ✅ Film ma wszystkie gatunki (kompletny)")
                        total_already_complete += 1

                    save_checkpoint(movie.title, i)

                    # Stats co 50 filmów
                    if current_number % 50 == 0:
                        print(f"\n📊 STATYSTYKI PO {current_number} FILMACH:")
                        print(f"   🔗 Dodanych relacji: {total_added_relations}")
                        print(f"   ✅ Kompletnych: {total_already_complete}")
                        print(f"   🚫 Bez gatunków TMDb: {total_no_genres}")
                        print(f"   ❌ Błędów: {total_errors}")
                        print(
                            f"   ⏰ Pozostało: {total_movies - current_number} filmów"
                        )

                    time.sleep(0.3)  # Rate limit

                except requests.RequestException as e:
                    print(f"   💥 Błąd HTTP: {str(e)}")
                    total_errors += 1
                    save_checkpoint(movie.title, i)
                    time.sleep(5)

                except Exception as e:
                    print(f"   💥 Błąd: {str(e)}")
                    db.session.rollback()
                    total_errors += 1
                    save_checkpoint(movie.title, i)

            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
                print(f"\n🗑️  Checkpoint usunięty - proces zakończony!")

            print(f"\n" + "=" * 80)
            print(f"🎉 PROCES ZAKOŃCZONY!")
            print(f"=" * 80)
            print(f"📊 Sprawdzonych filmów: {total_movies}")
            print(f"🔗 Dodanych relacji (brakujące): {total_added_relations}")
            print(f"✅ Filmów kompletnych: {total_already_complete}")
            print(f"🚫 Bez gatunków TMDb: {total_no_genres}")
            print(f"❌ Błędów: {total_errors}")

        except KeyboardInterrupt:
            print(f"\n\n⚠️  PRZERWANO (Ctrl+C)")
            print(f"💾 Checkpoint zapisany - można wznowić!")


if __name__ == "__main__":
    main()
