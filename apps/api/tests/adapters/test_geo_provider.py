import pytest

from app.adapters.geo.errors import GeoProviderConfigurationError
from app.adapters.geo.kakao_provider import KakaoGeoProvider
from app.adapters.geo.mock_provider import MockGeoProvider


def test_mock_geo_provider_returns_matching_items() -> None:
    provider = MockGeoProvider()

    items = provider.search(query="성수", search_type="place")

    assert items
    assert any(item.label == "성수역" for item in items)


def test_mock_geo_provider_returns_reverse_lookup() -> None:
    provider = MockGeoProvider()

    item = provider.reverse(latitude=37.5446, longitude=127.0557)

    assert item.label
    assert item.source == "mock_reverse"


def test_kakao_provider_requires_rest_api_key() -> None:
    with pytest.raises(GeoProviderConfigurationError):
        KakaoGeoProvider(rest_api_key=None)
