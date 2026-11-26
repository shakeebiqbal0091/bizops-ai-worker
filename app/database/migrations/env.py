from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings
from app.database.models import Base

config = context.config
target_metadata = Base.metadata


def _url() -> str:
    override = config.attributes.get("url")  # used by tests
    if override:
        return str(override)
    url = get_settings().migration_database_url
    if url is None:
        raise RuntimeError("BIZOPS_MIGRATION_DATABASE_URL is not set")
    return url.get_secret_value()


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()