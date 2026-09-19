from logging.config import fileConfig

from alembic import context

from apps.backend.core.config import settings
from apps.backend.database.connection import Base
import apps.backend.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
  fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
  context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  connectable = context.config.attributes.get("connection")
  if connectable is None:
    from sqlalchemy import create_engine
    connectable = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
  with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
