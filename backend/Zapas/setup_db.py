from backend.Zapas.database import engine
from backend.Zapas.models import Base

# Tworzymy wszystkie tabele na podstawie modeli
Base.metadata.create_all(engine)

print("Tabele zostały utworzone w bazie danych!")
