import requests

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
language = "pl-PL"


def get_top_100_movies_by_vote_count():
    movies = []
    pages_to_fetch = 10  
    for page in range(1, pages_to_fetch + 1):
        url = f"https://api.themoviedb.org/3/movie/popular"
        params = {"api_key": api_key, "language": language, "page": page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        movies.extend(data.get("results", []))

    movies_sorted = sorted(movies, key=lambda m: m.get("vote_count", 0), reverse=True)
    return movies_sorted[:100]


top_100_movies = get_top_100_movies_by_vote_count()
for movie in top_100_movies:
    print(movie.get("title"), "- vote count:", movie.get("vote_count"))
