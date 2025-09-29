import requests
import os
import time
import sys

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
CHECKPOINT_FILE = "movie_genres_checkpoint6.txt"

TMDB_TO_DB_GENRES = {
    "Action": 60,
    "Adventure": 60,
    "Animation": 52,
    "Comedy": 28,
    "Crime": 53,
    "Documentary": 12,
    "Drama": 15,
    "Family": 20,
    "Fantasy": 21,
    "History": 25,
    "Horror": 26,
    "Music": 28,
    "Mystery": 55,
    "Romance": 56,
    "Science Fiction": 48,
    "TV Movie": 12,
    "Thriller": 61,
    "War": 58,
    "Western": 59,
    "Akcja": 60,
    "Przygodowy": 60,
    "Animacja": 52,
    "Komedia": 28,
    "Kryminał": 53,
    "Kryminalne": 53,
    "Dokumentalny": 12,
    "Dramat": 15,
    "Dramat obyczajowy": 15,
    "Familijny": 20,
    "Dla całej rodziny": 20,
    "Fantasy": 21,
    "Fantastyczny": 21,
    "Historyczny": 25,
    "Historia": 25,
    "Horror": 26,
    "Muzyczny": 28,
    "Tajemnica": 55,
    "Romans": 56,
    "Romantyczny": 56,
    "Sci-Fi": 48,
    "Science Fiction": 48,
    "Film telewizyjny": 12,
    "Dreszczowiec": 17,
    "Thriller": 61,
    "Wojenny": 58,
    "Western": 59,
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
    "Katastroficzny": 27,
    "Disaster": 27,
    "Baśń": 5,
    "Fairy Tale": 5,
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
                    f"🔄 Checkpoint found: resuming from movie '{last_title}' (#{last_index + 1})"
                )
                return last_title, last_index
    return None, 0


def save_checkpoint(title, index):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{index}")


def count_movies_without_genres():
    count = (
        db.session.query(Movie)
        .outerjoin(MovieGenre, Movie.movie_id == MovieGenre.movie_id)
        .filter(MovieGenre.movie_id.is_(None))
        .count()
    )
    return count


def get_movies_without_genres():
    return (
        db.session.query(Movie)
        .outerjoin(MovieGenre, Movie.movie_id == MovieGenre.movie_id)
        .filter(MovieGenre.movie_id.is_(None))
        .order_by(Movie.movie_id)
        .all()
    )


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
        print(f"     ⚠️  Błąd wyszukiwania TMDb: {str(e)}")
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

        genres = details.get("genres", [])
        return genres

    except Exception as e:
        print(f"     ⚠️  Błąd pobierania szczegółów TMDb: {str(e)}")
        return []


def map_tmdb_genre_to_db(tmdb_genre_name):
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
        print("🎬 ROZPOCZYNAM WYSZUKIWANIE GATUNKÓW PRZEZ TMDb API")
        print("(Tylko filmy bez gatunków)")
        print("=" * 80)

        print("📊 Liczę filmy bez gatunków...")
        total_movies = count_movies_without_genres()
        print(f"📊 ZNALEZIONO {total_movies} FILMÓW BEZ GATUNKÓW")
        print("=" * 80)

        if total_movies == 0:
            print("🎉 Wszystkie filmy mają już przypisane gatunki!")
            return

        print("📋 Pobieram listę filmów bez gatunków...")
        movies_without_genres = get_movies_without_genres()

        print(f"📝 Przykłady filmów bez gatunków:")
        for i, movie in enumerate(movies_without_genres[:5]):
            print(f"   {i+1}. {movie.title} (ID: {movie.movie_id})")
        if total_movies > 5:
            print(f"   ... i {total_movies - 5} więcej")

        print("=" * 80)

        last_title, start_index = load_checkpoint()

        total_added_relations = 0
        total_skipped = 0
        total_errors = 0
        total_no_genres = 0

        try:
            for i in range(start_index, total_movies):
                movie = movies_without_genres[i]
                current_number = i + 1

                print(f"\n🎭 FILM {current_number} z {total_movies}: '{movie.title}'")
                print(
                    f"📈 POSTĘP: {current_number}/{total_movies} ({(current_number/total_movies*100):.1f}%)"
                )

                try:
                    movie_year = None
                    if hasattr(movie, "release_date") and movie.release_date:
                        movie_year = movie.release_date.year

                    print(f"   🔍 Szukam w TMDb...")
                    tmdb_movie_id = search_movie_in_tmdb(movie.title, movie_year)

                    if not tmdb_movie_id:
                        print(f"   ❌ Nie znaleziono filmu w TMDb")
                        total_no_genres += 1
                        save_checkpoint(movie.title, i)
                        continue

                    print(f"   ✅ Znaleziono w TMDb (ID: {tmdb_movie_id})")

                    print(f"   📋 Pobieram gatunki z TMDb...")
                    tmdb_genres = get_movie_genres_from_tmdb(tmdb_movie_id)

                    if not tmdb_genres:
                        print(f"   ❌ Brak gatunków w TMDb")
                        total_no_genres += 1
                        save_checkpoint(movie.title, i)
                        continue

                    print(f"   🎭 TMDb gatunki: {[g['name'] for g in tmdb_genres]}")

                    relations_added = 0
                    mapped_genres = []

                    for genre_data in tmdb_genres:
                        tmdb_genre_name = genre_data.get("name")
                        if not tmdb_genre_name:
                            continue

                        db_genre_id = map_tmdb_genre_to_db(tmdb_genre_name)

                        if not db_genre_id:
                            print(f"   ⚠️  Nie zmapowano gatunku: {tmdb_genre_name}")
                            continue

                        genre_exists = db.session.query(
                            db.session.query(Genre)
                            .filter_by(genre_id=db_genre_id)
                            .exists()
                        ).scalar()

                        if not genre_exists:
                            print(
                                f"   ⚠️  Gatunek ID {db_genre_id} nie istnieje w bazie"
                            )
                            continue

                        existing_relation = MovieGenre.query.filter_by(
                            movie_id=movie.movie_id, genre_id=db_genre_id
                        ).first()

                        if not existing_relation:
                            relation = MovieGenre(
                                movie_id=movie.movie_id, genre_id=db_genre_id
                            )
                            db.session.add(relation)
                            relations_added += 1
                            mapped_genres.append(f"{tmdb_genre_name} -> {db_genre_id}")

                    if relations_added > 0:
                        db.session.commit()
                        total_added_relations += relations_added
                        print(f"   💾 Dodano {relations_added} relacji:")
                        for mapped in mapped_genres:
                            print(f"     ✅ {mapped}")
                    else:
                        print(
                            f"   ⏭️  Wszystkie relacje już istnieją lub gatunki nie zostały zmapowane"
                        )
                        total_skipped += 1

                    save_checkpoint(movie.title, i)

                    if current_number % 10 == 0:
                        remaining = total_movies - current_number
                        print(f"\n📊 STATYSTYKI PO {current_number} FILMACH:")
                        print(f"   🔗 Dodanych relacji: {total_added_relations}")
                        print(f"   ⏭️  Pominiętych: {total_skipped}")
                        print(f"   🚫 Bez gatunków: {total_no_genres}")
                        print(f"   ❌ Błędów: {total_errors}")
                        print(
                            f"   📈 Postęp: {current_number}/{total_movies} ({(current_number/total_movies*100):.1f}%)"
                        )
                        print(f"   ⏰ Pozostało: {remaining} filmów")

                    time.sleep(0.5)

                except requests.RequestException as e:
                    print(f"   💥 Błąd HTTP: {str(e)}")
                    total_errors += 1
                    save_checkpoint(movie.title, i)
                    time.sleep(5)

                except Exception as e:
                    print(f"   💥 Niespodziewany błąd: {str(e)}")
                    db.session.rollback()
                    total_errors += 1
                    save_checkpoint(movie.title, i)

            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
                print(f"\n🗑️  Usunięto checkpoint - proces zakończony!")

            print(f"\n" + "=" * 80)
            print(f"🎉 PROCES ZAKOŃCZONY!")
            print(f"=" * 80)
            print(f"📊 Przetworzonych filmów: {total_movies}")
            print(f"🔗 Dodanych relacji: {total_added_relations}")
            print(f"⏭️  Pominiętych: {total_skipped}")
            print(f"🚫 Bez gatunków: {total_no_genres}")
            print(f"❌ Błędów: {total_errors}")
            if total_movies > 0:
                success_rate = (total_added_relations) / total_movies * 100
                print(f"🎯 Procent sukcesu: {success_rate:.1f}%")

        except KeyboardInterrupt:
            print(f"\n\n⚠️  PRZERWANO PRZEZ UŻYTKOWNIKA (Ctrl+C)")
            print(f"💾 Checkpoint został zapisany - można wznowić!")


if __name__ == "__main__":
    main()
