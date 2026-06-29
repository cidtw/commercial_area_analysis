from app.core.config import Settings


def test_settings_parse_allowed_origins_from_csv() -> None:
    settings = Settings(ALLOWED_ORIGINS="http://localhost:3000,http://example.com")

    assert settings.allowed_origins == [
        "http://localhost:3000",
        "http://example.com",
    ]

