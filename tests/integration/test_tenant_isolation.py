import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.database.models import Business, Task
from app.database.session import business_session


@pytest.fixture
def two_businesses(owner_engine: Engine) -> Iterator[tuple[uuid.UUID, uuid.UUID]]:
    def truncate() -> None:
        with owner_engine.begin() as conn:
            conn.execute(text("TRUNCATE businesses CASCADE"))

    truncate()
    with Session(owner_engine) as s, s.begin():
        a, b = Business(name="Alpha Store"), Business(name="Beta Store")
        s.add_all([a, b])
        s.flush()
        s.add_all([Task(business_id=a.id, title="A task"), Task(business_id=b.id, title="B task")])
        ids = (a.id, b.id)
    yield ids
    truncate()


def test_app_role_cannot_bypass_rls(app_engine: Engine) -> None:
    with app_engine.connect() as conn:
        row = conn.execute(
            text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
        ).one()
    assert tuple(row) == (False, False)


def test_session_sees_only_own_rows(app_engine: Engine, two_businesses) -> None:
    a, _ = two_businesses
    with business_session(a, app_engine) as s:
        assert s.scalars(select(Task.title)).all() == ["A task"]
        assert s.scalars(select(Business.name)).all() == ["Alpha Store"]


def test_no_context_fails_closed(app_engine: Engine, two_businesses) -> None:
    with app_engine.begin() as conn:
        assert conn.execute(text("SELECT count(*) FROM tasks")).scalar_one() == 0


def test_cross_tenant_insert_rejected(app_engine: Engine, two_businesses) -> None:
    a, b = two_businesses
    with pytest.raises(DBAPIError), business_session(a, app_engine) as s:
        s.add(Task(business_id=b, title="smuggled"))
        s.flush()


def test_context_does_not_leak_through_pool(app_engine: Engine, two_businesses) -> None:
    a, _ = two_businesses
    with business_session(a, app_engine) as s:
        assert s.scalars(select(Task)).all()
    with app_engine.begin() as conn:  # same single pooled connection
        assert conn.execute(text("SELECT count(*) FROM tasks")).scalar_one() == 0