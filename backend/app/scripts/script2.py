import requests
import time
import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import quote
from app import create_app
from app.extensions import db
from app.models.director import Director
from app.models.movie import Movie
from app.models.movie_director import MovieDirector

API_KEY = "d729e3223cb49b1d62ae3feb6a2cd2b7"
BASE_URL = "https://api.themoviedb.org/3"
LANGUAGE = "pl-PL"
CHECKPOINT_FILE = "movie_director_checkpoint3.txt"


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


def google_verify_director(movie_title, director_name, num_results=5):
    """Weryfikuje przez Google Search czy reżyser jest powiązany z filmem"""
    query = f'"{movie_title}" "{director_name}" director'
    print(f"     🔍 Weryfikuję Google: {query}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    search_url = (
        f"https://www.google.com/search?q={quote(query)}&hl=en&num={num_results}"
    )

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Sprawdź w tytułach i opisach wyników
        search_results = soup.find_all(
            ["h3", "span", "div"], class_=["LC20lb", "VwiC3b", "g"]
        )

        for result in search_results:
            result_text = result.get_text().lower()

            # Sprawdź czy zawiera nazwę filmu i reżysera
            if (
                movie_title.lower() in result_text
                and director_name.lower() in result_text
                and ("director" in result_text or "directed" in result_text)
            ):
                print(
                    f"     ✅ Google potwierdza: {director_name} reżyserował {movie_title}"
                )
                return True

        # Sprawdź także w linkach
        links = soup.find_all("a", href=True)
        for link in links[:num_results]:
            link_text = link.get("href", "").lower()
            if (
                movie_title.lower().replace(" ", "-") in link_text
                and director_name.lower().replace(" ", "-") in link_text
            ):
                print(f"     ✅ Google potwierdza przez URL")
                return True

        print(f"     ❌ Google NIE potwierdza: {director_name} dla {movie_title}")
        return False

    except Exception as e:
        print(f"     ⚠️  Błąd weryfikacji Google: {str(e)}")
        return True  # W razie błędu, akceptuj (żeby nie blokować procesu)


def get_person_details(person_id):
    url = f"{BASE_URL}/person/{person_id}"
    params = {"api_key": API_KEY, "language": LANGUAGE}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def sanitize(text):
    if not text:
        return ""
    return text.replace("\n", " ").replace("\r", " ").replace("'", "''").strip()


def search_movie_tmdb(title):
    params = {
        "api_key": API_KEY,
        "language": LANGUAGE,
        "query": title,
        "include_adult": False,
        "page": 1,
    }
    response = requests.get(f"{BASE_URL}/search/movie", params=params)
    response.raise_for_status()
    return response.json()


def get_movie_credits(tmdb_movie_id):
    url = f"{BASE_URL}/movie/{tmdb_movie_id}/credits"
    params = {"api_key": API_KEY, "language": LANGUAGE}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def find_first_suitable_director_with_verification(crew, movie_title):
    """Znajduje pierwszego reżysera z kompletnymi danymi + weryfikacja Google"""
    seen_directors = set()

    for person in crew:
        if person.get("known_for_department") == "Directing":
            director_name = person.get("name")
            person_id = person.get("id")

            if director_name in seen_directors:
                continue
            seen_directors.add(director_name)

            print(f"   🎪 Sprawdzam reżysera: {director_name}")

            # KROK 1: Sprawdź czy już jest w bazie
            existing_director = Director.query.filter_by(
                director_name=director_name
            ).first()
            if existing_director:
                # Weryfikuj Google nawet dla istniejących reżyserów
                if google_verify_director(movie_title, director_name):
                    print(
                        f"     ✅ Już jest w bazie + Google potwierdza (ID: {existing_director.director_id})"
                    )
                    return existing_director, True
                else:
                    print(
                        f"     ❌ Już jest w bazie ale Google NIE potwierdza - pomijam"
                    )
                    continue

            try:
                # KROK 2: Pobierz szczegóły z TMDB
                details = get_person_details(person_id)

                birth_date = details.get("birthday")
                birth_place = details.get("place_of_birth")
                biography = details.get("biography") or ""
                profile_path = details.get("profile_path")
                photo_url = (
                    f"https://image.tmdb.org/t/p/w500{profile_path}"
                    if profile_path
                    else ""
                )
                gender_code = details.get("gender", 0)
                gender = "K" if gender_code == 1 else "M" if gender_code == 2 else ""

                # KROK 3: Sprawdź wymagane pola
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
                    print(f"     ❌ Pominięty - brak: {', '.join(missing_fields)}")
                    continue

                # KROK 4: WERYFIKACJA GOOGLE - NAJWAŻNIEJSZE!
                if not google_verify_director(movie_title, director_name):
                    print(
                        f"     ❌ Google nie potwierdza - POMIJAM i szukam następnego"
                    )
                    continue  # Szukaj następnego reżysera!

                # KROK 5: Jeśli Google potwierdza - utwórz obiekt
                director_obj = Director(
                    director_name=sanitize(director_name),
                    birth_date=birth_date,
                    birth_place=sanitize(birth_place),
                    biography=sanitize(biography),
                    photo_url=photo_url,
                    gender=gender,
                )

                print(f"     ✅ Przygotowany do dodania (Google potwierdził!)")
                return director_obj, False

            except Exception as e:
                print(f"     💥 Błąd pobierania szczegółów: {str(e)}")
                continue

    return None, False


def main():
    app = create_app()

    with app.app_context():
        print("🎬 ROZPOCZYNAM WYSZUKIWANIE REŻYSERÓW Z WERYFIKACJĄ GOOGLE")
        print(
            "(Biorę tylko PIERWSZEGO reżysera z kompletnymi danymi + weryfikacja Google)"
        )
        print("=" * 80)

        movies_without_director = (
            db.session.query(Movie)
            .outerjoin(MovieDirector, Movie.movie_id == MovieDirector.movie_id)
            .filter(MovieDirector.movie_id.is_(None))
            .order_by(Movie.movie_id)
            .all()
        )

        total_movies = len(movies_without_director)
        print(f"📊 Znaleziono {total_movies} filmów bez reżysera")
        print("=" * 80)

        last_title, start_index = load_checkpoint()

        total_added_directors = 0
        total_added_relations = 0
        total_skipped = 0
        total_errors = 0
        total_google_rejected = 0  # Nowa statystyka

        try:
            for i in range(start_index, total_movies):
                movie = movies_without_director[i]
                current_number = i + 1

                print(f"\n🎭 Film {current_number} z {total_movies}: '{movie.title}'")

                try:
                    print(f"   🔍 Szukam w TMDB...")
                    search_data = search_movie_tmdb(movie.title)
                    results = search_data.get("results", [])

                    if not results:
                        print(f"   ❌ Film nie znaleziony w TMDB")
                        total_errors += 1
                        save_checkpoint(movie.title, i)
                        continue

                    tmdb_movie_id = results[0]["id"]
                    print(f"   ✅ Znaleziono w TMDB (ID: {tmdb_movie_id})")

                    print(f"   👥 Pobieram obsadę...")
                    credits_data = get_movie_credits(tmdb_movie_id)
                    crew = credits_data.get("crew", [])

                    # ZNAJDŹ PIERWSZEGO PASUJĄCEGO REŻYSERA + WERYFIKACJA GOOGLE
                    director, already_exists = (
                        find_first_suitable_director_with_verification(
                            crew, movie.title
                        )
                    )

                    if not director:
                        print(
                            f"   ❌ Nie znaleziono pasującego reżysera (po weryfikacji Google)"
                        )
                        total_google_rejected += 1
                        save_checkpoint(movie.title, i)
                        continue

                    # Dodaj do bazy i relacji
                    try:
                        if not already_exists:
                            db.session.add(director)
                            db.session.flush()
                            total_added_directors += 1
                            print(
                                f"   💾 Dodano nowego reżysera do bazy: {director.director_name}"
                            )
                        else:
                            print(
                                f"   ℹ️  Używam istniejącego reżysera: {director.director_name}"
                            )

                        existing_relation = MovieDirector.query.filter_by(
                            movie_id=movie.movie_id, director_id=director.director_id
                        ).first()

                        if not existing_relation:
                            relation = MovieDirector(
                                movie_id=movie.movie_id,
                                director_id=director.director_id,
                            )
                            db.session.add(relation)
                            db.session.commit()
                            total_added_relations += 1
                            print(f"   🔗 Dodano relację film-reżyser")
                        else:
                            print(f"   ⏭️  Relacja film-reżyser już istnieje")
                            total_skipped += 1

                    except Exception as e:
                        db.session.rollback()
                        print(f"   💥 Błąd zapisu do bazy: {str(e)}")
                        total_errors += 1
                        save_checkpoint(movie.title, i)
                        continue

                    save_checkpoint(movie.title, i)

                    # Statystyki co 5 filmów (rzadziej z powodu Google requests)
                    if current_number % 5 == 0:
                        print(f"\n📊 STATYSTYKI PO {current_number} FILMACH:")
                        print(f"   ✅ Dodanych reżyserów: {total_added_directors}")
                        print(f"   🔗 Dodanych relacji: {total_added_relations}")
                        print(f"   ⏭️  Pominiętych: {total_skipped}")
                        print(
                            f"   🚫 Odrzuconych przez Google: {total_google_rejected}"
                        )
                        print(f"   ❌ Błędów: {total_errors}")
                        print(f"   📈 Postęp: {(current_number/total_movies*100):.1f}%")

                    # Dłuższa pauza z powodu Google requests
                    time.sleep(3)

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
            print(f"✅ Dodanych reżyserów: {total_added_directors}")
            print(f"🔗 Dodanych relacji: {total_added_relations}")
            print(f"⏭️  Pominiętych: {total_skipped}")
            print(f"🚫 Odrzuconych przez Google: {total_google_rejected}")
            print(f"❌ Błędów: {total_errors}")
            if total_movies > 0:
                success_rate = (total_added_relations) / total_movies * 100
                print(f"🎯 Procent sukcesu: {success_rate:.1f}%")

        except KeyboardInterrupt:
            print(f"\n\n⚠️  PRZERWANO PRZEZ UŻYTKOWNIKA (Ctrl+C)")
            print(f"💾 Checkpoint został zapisany - można wznowić!")


if __name__ == "__main__":
    main()
