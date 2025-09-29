import os
from icrawler.builtin import BingImageCrawler
import re

# lista filmów
movies = [
    "Barbie",
    "Diuna",
    "Interstellar",
    "Joker",
    "Mickey17",
    "Saltburn",
    "Towarzysz",
    "Vaiana",
    "The Brutalist",
    "Kapitan Ameryka: Nowy wspaniały świat",
    "Bridget Jones: Szalejąc za facetem",
    "Fantastyczna Czwórka",
    "Guardians of the Galaxy Vol. 3",
    "Napoleon",
    "Killers of the Flower Moon",
    "Poor Things",
    "Wonka",
    "Oppenheimer",
    "Elemental",
    "The Marvels",
    "Wicked: Part One",
    "Tron: Ares",
    "Mission: Impossible – The Final Reckoning",
    "Jurassic World: Rebirth",
    "Superman",
    "Thunderbolts*",
    "Weapons",
    "The Smashing Machine",
    "Nobody 2",
    "Americana",
    "Caught Stealing",
    "Paddington in Peru",
    "Deadpool & Wolverine",
    "Sonic the Hedgehog 3",
    "Kraven the Hunter",
    "Moana 2",
    "Carry-On",
    "Mufasa: The Lion King",
    "The Lord of the Rings: The War of the Rohirrim",
    "Red One",
    "Gladiator II",
    "Beetlejuice Beetlejuice",
    "Smile 2",
    "Alien: Romulus",
    "Hellboy: The Crooked Man",
    "Joker: Folie à Deux",
    "Argylle",
    "Inside Out 2",
    "The Tiger's Apprentice",
    "Godzilla x Kong: The New Empire",
    "Moana",
    "Fences",
    "Marriage Story",
    "I, Tonya",
    "Bohemian Rhapsody",
    "Short Term 12",
    "Star Wars: The Force Awakens",
    "Wonder Woman",
    "Creed",
    "The Devil Wears Prada",
    "The Favourite",
    "Knives Out",
    "Widows",
    "Fantastic Beasts and Where to Find Them",
    "X-Men: First Class",
    "The Light Between Oceans",
    "Ex Machina",
    "The Imitation Game",
    "The Danish Girl",
    "The Theory of Everything",
    "Les Misérables",
    "Knives Out",
    "The Favourite",
    "Short Term 12",
    "Birdman",
    "Fences",
    "Marriage Story",
    "I, Tonya",
    "Bohemian Rhapsody",
    "The Devil Wears Prada",
    "Widows",
    "X-Men: Days of Future Past",
    "The Light Between Oceans",
    "Abigail",
    "Venom: The Last Dance",
]


# funkcja do snake_case
def title_to_filename(title: str) -> str:
    name = title.lower()
    translate = str.maketrans("ąćęłńóśźż", "acelnoszz")
    name = name.translate(translate)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return f"{name}.jpg"


# katalog na plakaty
os.makedirs("movies", exist_ok=True)

for movie in movies:
    print(f"Pobieram: {movie}...")

    filename = title_to_filename(movie)

    bing_crawler = BingImageCrawler(storage={"root_dir": "movies"})
    bing_crawler.crawl(
        keyword=f"{movie} movie poster",  # 🎯 szukamy plakatu filmowego
        max_num=3,
        min_size=(300, 300),
    )

    # zmiana nazwy
    renamed = False
    for f in os.listdir("movies"):
        if f.lower().endswith((".jpg", ".png")) and not f.startswith(filename):
            try:
                os.rename(os.path.join("movies", f), os.path.join("movies", filename))
                renamed = True
                break
            except FileExistsError:
                renamed = True
                break

    if not renamed:
        print(f"⚠️ Nie udało się pobrać plakatu dla: {movie}")
