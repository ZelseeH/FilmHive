import os
import time
from youtubesearchpython import VideosSearch
from app import create_app
from app.models.movie import Movie
from app.extensions import db

CHECKPOINT_FILE = "update_trailers_checkpoint.txt"


def load_checkpoint():
    """Ładuje ostatni przetworzony film z checkpointu"""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                lines = content.split("\n")
                last_title = lines[0]
                last_index = int(lines[1]) if len(lines) > 1 else 0
                return last_title, last_index
    return None, 0


def save_checkpoint(title, index):
    """Zapisuje checkpoint z nazwą filmu i indeksem"""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{index}")


def search_youtube_trailer(movie_title, retries=3):
    """Wyszukuje trailer na YouTube"""
    query = f"{movie_title} trailer"

    for attempt in range(retries):
        try:
            videos_search = VideosSearch(query, limit=1)
            results = videos_search.result()

            if results and "result" in results and len(results["result"]) > 0:
                first_video = results["result"][0]
                video_link = first_video.get("link")
                if video_link:
                    return video_link

        except Exception as e:
            print(f"    ⚠️  Błąd wyszukiwania (próba {attempt + 1}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)

    return None


def update_movie_trailers():
    """Główna funkcja aktualizująca trailery"""
    app = create_app()

    with app.app_context():
        try:
            # Pobierz wszystkie filmy posortowane po tytule
            movies = Movie.query.order_by(Movie.title.asc()).all()
            total_movies = len(movies)
            updated_count = 0
            skipped_count = 0

            print(f"🎬 ROZPOCZYNAM AKTUALIZACJĘ TRAILERÓW")
            print(f"📊 Całkowita liczba filmów: {total_movies}")
            print("=" * 80)

            # Sprawdź checkpoint
            last_title, start_index = load_checkpoint()

            if last_title and start_index > 0:
                print(f"🔄 WZNAWIAM z checkpointu:")
                print(f"   Ostatni przetworzony film: '{last_title}'")
                print(f"   Zaczynam od filmu #{start_index + 1}")
                print("=" * 80)
            else:
                print(f"🚀 ROZPOCZYNAM od początku")
                print("=" * 80)

            # Przetwarzaj filmy od checkpointu
            for i in range(start_index, total_movies):
                movie = movies[i]
                current_number = i + 1

                print(f"\n🎭 Film {current_number} z {total_movies}: '{movie.title}'")

                # Sprawdź czy film już ma trailer
                if movie.trailer_url and movie.trailer_url.strip():
                    print(f"   ⏭️  Film już ma trailer - POMIJAM")
                    print(f"   🔗 Istniejący URL: {movie.trailer_url}")
                    skipped_count += 1
                    save_checkpoint(movie.title, i)
                    continue

                # Wyszukaj trailer na YouTube
                print(f"   🔍 Szukam trailera na YouTube...")
                trailer_url = search_youtube_trailer(movie.title)

                if trailer_url:
                    try:
                        # Aktualizuj bazę danych
                        movie.trailer_url = trailer_url
                        db.session.commit()
                        updated_count += 1

                        print(f"   ✅ DODANO DO BAZY!")
                        print(f"   🔗 URL: {trailer_url}")

                    except Exception as e:
                        db.session.rollback()
                        print(f"   💥 Błąd zapisu do bazy: {str(e)}")

                else:
                    print(f"   ❌ Nie znaleziono trailera")

                # Zapisz checkpoint po każdym filmie
                save_checkpoint(movie.title, i)

                # Wyświetl statystyki co 10 filmów
                if current_number % 10 == 0:
                    print(f"\n📊 STATYSTYKI PO {current_number} FILMACH:")
                    print(f"   ✅ Dodane trailery: {updated_count}")
                    print(f"   ⏭️  Pominięte: {skipped_count}")
                    print(f"   📈 Postęp: {(current_number/total_movies*100):.1f}%")

                # Pauza między requestami (ważne dla YouTube API)
                if i < total_movies - 1:  # Nie czekaj po ostatnim
                    time.sleep(2)

            # Usuń checkpoint po zakończeniu
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
                print(f"\n🗑️  Usunięto checkpoint - proces zakończony!")

            # Końcowe podsumowanie
            print(f"\n" + "=" * 80)
            print(f"🎉 PROCES ZAKOŃCZONY POMYŚLNIE!")
            print(f"=" * 80)
            print(f"📊 Całkowita liczba filmów: {total_movies}")
            print(f"✅ Dodano nowych trailerów: {updated_count}")
            print(f"⏭️  Pominięto (już miały): {skipped_count}")
            print(f"❌ Nie znaleziono: {total_movies - updated_count - skipped_count}")
            print(
                f"🎯 Procent sukcesu: {(updated_count / (total_movies - skipped_count) * 100):.1f}%"
            )

        except KeyboardInterrupt:
            print(f"\n\n⚠️  PRZERWANO PRZEZ UŻYTKOWNIKA (Ctrl+C)")
            print(f"💾 Checkpoint został zapisany - można wznowić later!")
            print(f"🔄 Aby wznowić, uruchom skrypt ponownie")

        except Exception as e:
            print(f"\n💥 KRYTYCZNY BŁĄD: {str(e)}")
            print(f"💾 Checkpoint został zapisany")
            db.session.rollback()


def show_progress():
    """Pokaż postęp z checkpointu"""
    last_title, start_index = load_checkpoint()

    if last_title:
        app = create_app()
        with app.app_context():
            total_movies = Movie.query.count()
            progress_percent = (start_index / total_movies) * 100

            print(f"📊 AKTUALNY POSTĘP:")
            print(f"   Ostatni przetworzony: '{last_title}'")
            print(f"   Indeks: {start_index + 1} z {total_movies}")
            print(f"   Postęp: {progress_percent:.1f}%")
    else:
        print(f"❌ Brak checkpointu - nie rozpoczęto jeszcze procesu")


def reset_checkpoint():
    """Resetuj checkpoint i zacznij od nowa"""
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print(
            f"🗑️  Checkpoint został usunięty - następne uruchomienie zacznie od początku"
        )
    else:
        print(f"❌ Brak checkpointu do usunięcia")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "progress":
            show_progress()
        elif sys.argv[1] == "reset":
            reset_checkpoint()
        else:
            print(f"Użycie:")
            print(f"  python {sys.argv[0]}           # uruchom aktualizację")
            print(f"  python {sys.argv[0]} progress  # pokaż postęp")
            print(f"  python {sys.argv[0]} reset     # resetuj checkpoint")
    else:
        update_movie_trailers()
