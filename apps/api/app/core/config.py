from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_url: str = Field(
        default="sqlite:///./commercial_area_analysis.db",
        alias="DATABASE_URL",
    )
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://127.0.0.1:3000", "http://localhost:3000"],
        alias="ALLOWED_ORIGINS",
    )
    mock_data_label: str = Field(default="mock sample data", alias="MOCK_DATA_LABEL")
    geo_provider: Literal["mock", "kakao"] = Field(default="mock", alias="GEO_PROVIDER")
    kakao_local_rest_api_key: str | None = Field(default=None, alias="KAKAO_LOCAL_REST_API_KEY")
    next_public_map_provider: str = Field(default="mock", alias="NEXT_PUBLIC_MAP_PROVIDER")
    next_public_kakao_map_app_key: str | None = Field(
        default=None,
        alias="NEXT_PUBLIC_KAKAO_MAP_APP_KEY",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
