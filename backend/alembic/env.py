from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from alembic import context

# Dodaj ścieżkę do katalogu głównego projektu, aby importy działały poprawnie
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importujemy modele i metadane
from app.models.base import Base
import app.models  # Importuje wszystkie modele, aby były dostępne dla migracji

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ustawiamy target_metadata na metadane modeli
target_metadata = Base.metadata

# Funkcja do pobierania URL bazy danych z environment variables
def get_url():
    return os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:ZelseeH2001@localhost:5432/filmhive")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(get_url())

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
