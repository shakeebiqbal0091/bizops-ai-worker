from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Engine for the restricted application role (RLS enforced)."""
    url = get_settings().database_url
    if url is None:
        raise RuntimeError("BIZOPS_DATABASE_URL is not set")
    return create_engine(url.get_secret_value(), pool_pre_ping=True)


@contextmanager
def business_session(business_id: UUID, engine: Engine | None = None) -> Iterator[Session]:
    """Open a session scoped to one business.

    The whole block is ONE transaction: commits on success, rolls back on error.
    `app.current_business_id` is transaction-local (set_config(..., true)), so it
    cannot leak to the next user of a pooled connection. Use session.flush(),
    never session.commit(), inside the block.
    """
    factory = sessionmaker(engine or get_engine(), expire_on_commit=False)
    with factory() as session, session.begin():
        session.execute(
            text("SELECT set_config('app.current_business_id', :bid, true)"),
            {"bid": str(business_id)},
        )
        yield session