from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlmodel import SQLModel
from alembic import context
import os

# We import(dynamicly) our models so alembic can detect them(for changes migrations)
from src.models import *

# use the logic below if no Model s imported in the models package through its __init__.py file
""" import importlib
import pkgutil
import src.models as models

for _, name, _ in pkgutil.iter_modules(models.__path__):
    importlib.import_module(f"src.models.{name}") """

# Sync Postgres database connection url
ALEMBIC_DATABASE_URL = os.getenv(
    "ALEMBIC_DATABASE_URL",
    "postgresql://postgres:admin2025@localhost:5432/test_db1"
    )

# Async engine
engine = create_engine(ALEMBIC_DATABASE_URL, echo = False, future = True)
target_metadata = SQLModel.metadata


# We init alembic config object
config = context.config

# We configure loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = str(engine.url)
    context.configure(
        url = url,
        target_metadata = target_metadata,
        literal_binds = True,
        compare_type = True
        )

    with context.begin_transaction():
        context.run_migrations

def run_migrations_online():
    """Run migrations in 'online' mode."""
    with engine.connect() as connection:
        context.configure(
            connection = connection,
            target_metadata = target_metadata,
            compare_type = True
            )
        
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()