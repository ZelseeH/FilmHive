import requests

api_key = "d729e3223cb49b1d62ae3feb6a2cd2b7"
base_url = "https://api.themoviedb.org/3"
language = "pl-PL"


def get_total_popular_actors():
    url = f"{base_url}/person/popular"
    params = {
        "api_key": api_key,
        "language": language,
        "page": 1,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("total_results", "Brak danych")


if __name__ == "__main__":
    total = get_total_popular_actors()
    print(f"Łączna liczba popularnych aktorów w TMDb: {total}")
