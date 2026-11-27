import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine

OWNER_URL = os.environ.get(
    "BIZOPS_TEST_MIGRATION_DATABASE_URL",
    "postgresql+psycopg://bizops_owner:bizops_owner_dev@127.0.0.1:55432/bizops_test",
)
APP_URL = os.environ.get(
    "BIZOPS_TEST_DATABASE_URL",
    "postgresql+psycopg://bizops_app:bizops_app_dev@127.0.0.1:55432/bizops_test",
)


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    cfg = Config("alembic.ini")  # run pytest from the repo root
    cfg.attributes["url"] = OWNER_URL
    return cfg


@pytest.fixture(scope="session")
def owner_engine(alembic_config: Config) -> Iterator[Engine]:
    """Superuser/owner engine: migrations and test data setup only (bypasses RLS)."""
    command.upgrade(alembic_config, "head")
    engine = create_engine(OWNER_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def app_engine(owner_engine: Engine) -> Iterator[Engine]:
    """Restricted application role. Pool of 1 so any context leak would show up."""
    engine = create_engine(APP_URL, pool_size=1, max_overflow=0)
    yield engine
    engine.dispose()
