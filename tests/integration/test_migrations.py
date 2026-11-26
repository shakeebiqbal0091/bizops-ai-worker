from alembic import command
from alembic.config import Config
from sqlalchemy import Engine


def test_upgrade_downgrade_roundtrip(owner_engine: Engine, alembic_config: Config) -> None:
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")


def test_models_match_migrations(owner_engine: Engine, alembic_config: Config) -> None:
    command.check(alembic_config)  # raises if models drift from the migration