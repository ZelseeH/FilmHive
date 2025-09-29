import os
from icrawler.builtin import BingImageCrawler

actors = [
    "Barry Keoghan",
    "David Jonsson",
    "Joaquin Phoenix",
    "Timothée Chalamet",
    "Aulii Cravalho",
    "Sophie Wilde",
    "Levee Duplay",
    "Zendaya",
    "Anne Hathaway",
    "Pedro Pascal",
    "Michael Fassbender",
    "Daniel Brühl",
    "Chris Hemsworth",
    "Eddie Redmayne",
    "Emma Watson",
    "Lupita Nyong’o",
    "Margot Robbie",
    "Rami Malek",
    "Brie Larson",
    "John Boyega",
    "Gal Gadot",
    "Michael B. Jordan",
    "Elizabeth Debicki",
    "Florence Pugh",
    "Zazie Beetz",
    "Dev Patel",
    "Rosamund Pike",
    "Idris Elba",
    "Awkwafina",
    "Oscar Isaac",
    "Saoirse Ronan",
    "Tom Holland",
    "Ke Huy Quan",
    "Kirsten Dunst",
    "Paul Mescal",
    "Anya Taylor-Joy",
    "Andrew Garfield",
    "Yalitza Aparicio",
    "Mahershala Ali",
    "Tessa Thompson",
    "Lakeith Stanfield",
    "Tilda Swinton",
    "Javier Bardem",
    "Cate Blanchett",
    "Gael García Bernal",
    "Penélope Cruz",
    "Daniel Kaluuya",
    "Charlize Theron",
    "Benedict Cumberbatch",
    "Alicia Vikander",
    "Steven Yeun",
    "Natalie Portman",
    "Chadwick Boseman",
    "Emma Stone",
    "Donnie Yen",
    "Gemma Chan",
    "Adam Sandler",
    "Alisha Weir",
    "Melissa Barrera",
    "Dan Stevens",
    "Adam Driver",
]

# katalog na zdjęcia
os.makedirs("actors", exist_ok=True)

for actor in actors:
    print(f"Pobieram: {actor}...")

    # nazwa pliku np. "BrieLarson.jpg"
    filename = (
        actor.replace(" ", "")
        .replace(".", "")
        .replace("’", "")
        .replace("ñ", "n")
        .replace("ó", "o")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ú", "u")
        .replace("ö", "o")
        .replace("ü", "u")
        .replace("ß", "ss")
        + ".jpg"
    )

    # crawler Bing
    bing_crawler = BingImageCrawler(storage={"root_dir": "actors"})
    bing_crawler.crawl(
        keyword=actor,
        max_num=3,  # pobierz kilka, na wszelki wypadek
        min_size=(200, 200),
    )

    # zmiana nazwy pierwszego znalezionego pliku
    renamed = False
    for f in os.listdir("actors"):
        if f.lower().endswith((".jpg", ".png")) and not f.startswith(
            actor.replace(" ", "")
        ):
            try:
                os.rename(os.path.join("actors", f), os.path.join("actors", filename))
                renamed = True
                break
            except FileExistsError:
                # jeśli plik już istnieje, to pomijamy
                renamed = True
                break

    if not renamed:
        print(f"⚠️ Nie udało się zapisać zdjęcia dla: {actor}")
