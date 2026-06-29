from __future__ import annotations

from dataclasses import asdict

from app.adapters.geo.base import GeoSearchType
from app.adapters.geo.errors import GeoProviderValidationError
from app.adapters.geo.registry import build_geo_provider
from app.core.config import get_settings
from app.schemas.geo import GeoReverseResponse, GeoSearchItemResponse, GeoSearchResponse


def search_locations(*, query: str, search_type: GeoSearchType) -> GeoSearchResponse:
    normalized_query = query.strip()
    if not normalized_query:
        raise GeoProviderValidationError("The query parameter `q` is required.")
    provider = build_geo_provider(get_settings())
    items = provider.search(query=normalized_query, search_type=search_type)
    return GeoSearchResponse(
        query=normalized_query,
        type=search_type,
        items=[GeoSearchItemResponse(**asdict(item)) for item in items],
    )


def reverse_geocode(*, latitude: float, longitude: float) -> GeoReverseResponse:
    provider = build_geo_provider(get_settings())
    item = provider.reverse(latitude=latitude, longitude=longitude)
    return GeoReverseResponse(**asdict(item))
