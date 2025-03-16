from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Genre

# Połączenie z bazą danych
DATABASE_URL = "postgresql+psycopg2://postgres:ZelseeH2001@localhost:5432/filmhive"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Lista gatunków ze zrzutu ekranu
genres = [
    "Akcja", "Animacja", "Animacja dla dorosłych", "Anime", "Baśń", "Biblijny",
    "Biograficzny", "Czarna komedia", "Dla dzieci", "Dla młodzieży",
    "Dokumentalizowany", "Dokumentalny", "Dramat", "Dramat historyczny",
    "Dramat obyczajowy", "Dramat sądowy", "Dreszczowiec", "Erotyczny",
    "Fabularyzowany dok.", "Familijny", "Fantasy", "Film-Noir",
    "Gangsterski", "Groteska filmowa", "Historyczny", "Horror",
    "Katastroficzny", "Komedia", "Komedia kryminalna", "Komedia rom."
]

# Dodawanie gatunków do bazy danych
for genre_name in genres:
    genre = Genre(genre_name=genre_name)
    session.add(genre)

# Zatwierdzenie zmian
session.commit()

print("Gatunki zostały dodane do bazy danych!")
