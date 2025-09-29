import time
import requests
import random
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.movie import Movie
from app.models.user import User
from app.models.rating import Rating

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"


def search_movie_tmdb(title):
    """Wyszukuje film w TMDB API po tytule"""
    url = f"{base_url}/search/movie"
    params = {"api_key": api_key, "language": language, "query": title, "page": 1}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if results:
            movie = results[0]
            vote_average = movie.get("vote_average", 0)
            return vote_average
        else:
            print(f"Nie znaleziono filmu: {title}")
            return None

    except Exception as e:
        print(f"Błąd podczas szukania filmu '{title}': {str(e)}")
        return None


def generate_ratings_for_target_average(tmdb_average, num_ratings):
    """Generuje oceny tak, żeby średnia była zbliżona do TMDB na skali 1-10"""
    if tmdb_average == 0:
        return [random.randint(1, 10) for _ in range(num_ratings)]

    # ZMIANA: Nie konwertujemy skali - TMDB też używa 0-10, my 1-10
    # Jeśli TMDB ma 0, my dajemy minimum 1
    target_average = max(1, tmdb_average)

    # Generujemy oceny wokół średniej
    ratings = []

    # Pierwszy etap - generujemy większość ocen blisko średniej
    for i in range(num_ratings - 1):
        # Losowa wartość w przedziale ±2 od średniej
        rating = target_average + random.uniform(-2, 2)
        rating = max(1, min(10, round(rating)))
        ratings.append(rating)

    # Ostatnia ocena - dostosowujemy żeby osiągnąć dokładną średnią
    current_sum = sum(ratings)
    needed_rating = (target_average * num_ratings) - current_sum
    needed_rating = max(1, min(10, round(needed_rating)))
    ratings.append(needed_rating)

    # Sprawdzamy czy średnia jest w akceptowalnym zakresie (±0.5)
    actual_average = sum(ratings) / len(ratings)
    if abs(actual_average - target_average) > 0.5:
        # Jeśli nie, robimy drobne korekty
        attempts = 0
        while abs(sum(ratings) / len(ratings) - target_average) > 0.5 and attempts < 50:
            # Znajdź ocenę do zmiany
            for i in range(len(ratings)):
                current_avg = sum(ratings) / len(ratings)
                if current_avg < target_average - 0.5 and ratings[i] < 10:
                    ratings[i] += 1
                    break
                elif current_avg > target_average + 0.5 and ratings[i] > 1:
                    ratings[i] -= 1
                    break
            else:
                break
            attempts += 1

    return ratings


def add_ratings_for_movie(movie_id, tmdb_average, all_users):
    """Dodaje losową liczbę ocen dla filmu z kontrolowaną średnią"""
    if not all_users:
        print(f"Brak użytkowników w bazie danych")
        return 0

    max_users = len(all_users)
    num_ratings = random.randint(2, max_users)

    # Losujemy użytkowników którzy będą oceniać
    selected_users = random.sample(all_users, num_ratings)

    # Generujemy oceny dla osiągnięcia określonej średniej
    rating_values = generate_ratings_for_target_average(tmdb_average, num_ratings)

    ratings_to_add = []

    for i, user in enumerate(selected_users):
        # Sprawdzamy czy użytkownik już nie ocenił tego filmu
        existing_rating = Rating.query.filter_by(
            user_id=user.user_id, movie_id=movie_id
        ).first()

        if not existing_rating and i < len(rating_values):
            rating = Rating(
                user_id=user.user_id,
                movie_id=movie_id,
                rating=rating_values[i],
                rated_at=datetime.now(),
            )
            ratings_to_add.append(rating)

    if ratings_to_add:
        db.session.add_all(ratings_to_add)
        db.session.commit()

        # Wyświetlamy statystyki
        actual_average = sum([r.rating for r in ratings_to_add]) / len(ratings_to_add)
        target_average = max(1, tmdb_average)
        print(
            f"  TMDB: {tmdb_average:.2f}, Cel: {target_average:.2f}, Rzeczywista: {actual_average:.2f}, Różnica: {abs(actual_average - target_average):.2f}"
        )

    return len(ratings_to_add)


if __name__ == "__main__":
    app = create_app()
    with app.app_context():

        print("Pobieranie wszystkich filmów z bazy danych...")
        all_movies = Movie.query.all()
        print(f"Znaleziono {len(all_movies)} filmów")

        print("Pobieranie wszystkich użytkowników z bazy danych...")
        all_users = User.query.all()
        print(f"Znaleziono {len(all_users)} użytkowników")

        if not all_users:
            print("Brak użytkowników w bazie! Zakończenie skryptu.")
            exit()

        total_ratings_added = 0

        for i, movie in enumerate(all_movies, 1):
            print(f"\nPrzetwarzanie filmu {i}/{len(all_movies)}: {movie.title}")

            # Szukamy filmu w TMDB
            tmdb_average = search_movie_tmdb(movie.title)

            if tmdb_average is not None:
                print(f"Średnia ocena w TMDB: {tmdb_average}")

                # Dodajemy oceny dla tego filmu
                ratings_added = add_ratings_for_movie(
                    movie.movie_id, tmdb_average, all_users
                )

                total_ratings_added += ratings_added
                print(f"Dodano {ratings_added} ocen dla filmu '{movie.title}'")
            else:
                print(f"Pominięto film '{movie.title}' - brak danych z TMDB")

            # Pauza między requestami żeby nie przeciążać API
            time.sleep(0.5)

        print(f"\nKoniec! Łącznie dodano {total_ratings_added} ocen do bazy danych.")
