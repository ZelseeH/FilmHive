from database import engine
from models import Base

# Tworzymy wszystkie tabele na podstawie modeli
Base.metadata.create_all(engine)

print("Tabele zostały utworzone w bazie danych!")
