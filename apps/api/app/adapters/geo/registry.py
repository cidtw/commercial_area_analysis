from __future__ import annotations

from typing import Literal

from app.adapters.geo.base import GeoProvider
from app.adapters.geo.kakao_provider import KakaoGeoProvider
from app.adapters.geo.mock_provider import MockGeoProvider
from app.core.config import Settings

GeoProviderName = Literal["mock", "kakao"]


def build_geo_provider(settings: Settings) -> GeoProvider:
    if settings.geo_provider == "kakao":
        return KakaoGeoProvider(rest_api_key=settings.kakao_local_rest_api_key)
    return MockGeoProvider()
