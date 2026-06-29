from __future__ import annotations

from collections.abc import Sequence

from app.adapters.geo.base import GeoProvider, GeoSearchItem, GeoSearchType, ReverseGeocodeItem

MOCK_SEARCH_ITEMS: tuple[GeoSearchItem, ...] = (
    GeoSearchItem(
        label="성수역",
        source="mock_place",
        latitude=37.5446,
        longitude=127.0557,
        address="서울 성동구 아차산로 100",
        region="서울 성동구 성수동2가",
    ),
    GeoSearchItem(
        label="성수동 카페거리",
        source="mock_region",
        latitude=37.5441,
        longitude=127.0567,
        address="서울 성동구 성수이로7길 일대",
        region="서울 성동구 성수동2가",
    ),
    GeoSearchItem(
        label="서울숲",
        source="mock_place",
        latitude=37.5444,
        longitude=127.0374,
        address="서울 성동구 뚝섬로 273",
        region="서울 성동구 성수동1가",
    ),
)


class MockGeoProvider(GeoProvider):
    def __init__(self, items: Sequence[GeoSearchItem] | None = None) -> None:
        self._items = tuple(items) if items is not None else MOCK_SEARCH_ITEMS

    def search(self, *, query: str, search_type: GeoSearchType) -> list[GeoSearchItem]:
        query_lower = query.lower()
        filtered = [
            item
            for item in self._items
            if query_lower in item.label.lower()
            or (item.address is not None and query_lower in item.address.lower())
            or (item.region is not None and query_lower in item.region.lower())
        ]
        if search_type == "region":
            filtered.sort(key=lambda item: 0 if item.region is not None else 1)
        elif search_type == "address":
            filtered.sort(key=lambda item: 0 if item.address is not None else 1)
        return filtered[:8]

    def reverse(self, *, latitude: float, longitude: float) -> ReverseGeocodeItem:
        closest = min(
            self._items,
            key=lambda item: abs(item.latitude - latitude) + abs(item.longitude - longitude),
        )
        return ReverseGeocodeItem(
            label=closest.label,
            source="mock_reverse",
            latitude=latitude,
            longitude=longitude,
            address=closest.address,
            region=closest.region,
        )
