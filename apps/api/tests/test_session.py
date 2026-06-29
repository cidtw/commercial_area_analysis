from app.db.session import get_engine_kwargs


def test_sqlite_engine_kwargs_enable_cross_thread_access() -> None:
    kwargs = get_engine_kwargs("sqlite:///./commercial_area_analysis.db")

    assert kwargs["connect_args"] == {"check_same_thread": False}
    assert "pool_pre_ping" not in kwargs
    assert kwargs["future"] is True


def test_postgres_engine_kwargs_enable_pre_ping() -> None:
    kwargs = get_engine_kwargs("postgresql+psycopg://user:pass@localhost:5432/app")

    assert kwargs["connect_args"] == {}
    assert kwargs["pool_pre_ping"] is True
    assert kwargs["future"] is True
