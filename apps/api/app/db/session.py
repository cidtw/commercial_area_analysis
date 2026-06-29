from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def get_engine_kwargs(database_url: str) -> dict[str, object]:
    is_sqlite = database_url.startswith("sqlite")
    connect_args: dict[str, object] = {}
    if is_sqlite:
        connect_args["check_same_thread"] = False

    engine_kwargs: dict[str, object] = {
        "connect_args": connect_args,
        "future": True,
    }
    if not is_sqlite:
        engine_kwargs["pool_pre_ping"] = True
    return engine_kwargs


def build_engine(database_url: str) -> Engine:
    return create_engine(database_url, **get_engine_kwargs(database_url))


settings = get_settings()
engine = build_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
