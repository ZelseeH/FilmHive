from sqlalchemy import create_engine

# Połączenie z bazą danych
DATABASE_URL = "postgresql+psycopg2://postgres:ZelseeH2001@localhost:5432/filmhive"
engine = create_engine(DATABASE_URL)

# Sprawdzanie połączenia
try:
    with engine.connect() as connection:
        print("Połączono z bazą danych!")
except Exception as e:
    print(f"Błąd podczas łączenia z bazą danych: {e}")
