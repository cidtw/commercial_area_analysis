from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

GeoSearchType = Literal["address", "place", "region"]


@dataclass(frozen=True, slots=True)
class GeoSearchItem:
    label: str
    source: str
    latitude: float
    longitude: float
    address: str | None = None
    region: str | None = None


@dataclass(frozen=True, slots=True)
class ReverseGeocodeItem:
    label: str
    source: str
    latitude: float
    longitude: float
    address: str | None = None
    region: str | None = None


class GeoProvider(Protocol):
    def search(self, *, query: str, search_type: GeoSearchType) -> list[GeoSearchItem]:
        ...

    def reverse(self, *, latitude: float, longitude: float) -> ReverseGeocodeItem:
        ...
