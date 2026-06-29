from sqlalchemy import select

from app.bootstrap.mock_seed import ensure_mock_seeded
from app.db.models import Area, BusinessCategory, Store


def test_ensure_mock_seeded_populates_empty_database(db_session) -> None:
    db_session.query(Store).delete()
    db_session.query(BusinessCategory).delete()
    db_session.query(Area).delete()
    db_session.commit()

    ensure_mock_seeded(db_session)

    assert db_session.scalar(select(Area.id).limit(1)) is not None
    assert db_session.scalar(select(BusinessCategory.id).limit(1)) is not None
    assert db_session.scalar(select(Store.id).limit(1)) is not None


def test_ensure_mock_seeded_is_idempotent(db_session) -> None:
    first_count = db_session.query(Area).count()

    ensure_mock_seeded(db_session)

    assert db_session.query(Area).count() == first_count
