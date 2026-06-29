from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.adapters.geo.base import GeoProvider, GeoSearchItem, GeoSearchType, ReverseGeocodeItem
from app.adapters.geo.errors import (
    GeoProviderConfigurationError,
    GeoProviderRequestError,
)

KAKAO_LOCAL_BASE_URL = "https://dapi.kakao.com"


class KakaoGeoProvider(GeoProvider):
    def __init__(self, *, rest_api_key: str | None) -> None:
        if rest_api_key is None or not rest_api_key.strip():
            raise GeoProviderConfigurationError("Kakao Local REST API key is not configured.")
        self._rest_api_key = rest_api_key

    def search(self, *, query: str, search_type: GeoSearchType) -> list[GeoSearchItem]:
        if search_type == "address":
            path = "/v2/local/search/address.json"
        else:
            path = "/v2/local/search/keyword.json"
        payload = self._request(path=path, params={"query": query})
        documents = payload.get("documents", [])
        if not isinstance(documents, list):
            return []
        items: list[GeoSearchItem] = []
        for entry in documents:
            if not isinstance(entry, dict):
                continue
            latitude = _float_value(entry.get("y"))
            longitude = _float_value(entry.get("x"))
            if latitude is None or longitude is None:
                continue
            label = _first_text(entry, ("place_name", "address_name", "road_address_name"), fallback=query)
            items.append(
                GeoSearchItem(
                    label=label,
                    source=f"kakao_{search_type}",
                    latitude=latitude,
                    longitude=longitude,
                    address=_nullable_text(entry.get("address_name")),
                    region=_nullable_text(entry.get("road_address_name"))
                    or _nullable_text(entry.get("address_name")),
                )
            )
        return items

    def reverse(self, *, latitude: float, longitude: float) -> ReverseGeocodeItem:
        payload = self._request(
            path="/v2/local/geo/coord2address.json",
            params={"x": str(longitude), "y": str(latitude)},
        )
        documents = payload.get("documents", [])
        if not isinstance(documents, list) or not documents:
            raise GeoProviderRequestError("Kakao reverse geocoding returned no documents.")
        first = documents[0]
        if not isinstance(first, dict):
            raise GeoProviderRequestError("Kakao reverse geocoding returned an invalid document.")
        road_address = first.get("road_address")
        address = first.get("address")
        address_name = None
        region_name = None
        if isinstance(road_address, dict):
            address_name = _nullable_text(road_address.get("address_name"))
        if isinstance(address, dict):
            region_name = " ".join(
                part
                for part in (
                    _nullable_text(address.get("region_1depth_name")),
                    _nullable_text(address.get("region_2depth_name")),
                    _nullable_text(address.get("region_3depth_name")),
                )
                if part
            ) or None
            if address_name is None:
                address_name = _nullable_text(address.get("address_name"))
        return ReverseGeocodeItem(
            label=address_name or region_name or "선택 위치",
            source="kakao_reverse",
            latitude=latitude,
            longitude=longitude,
            address=address_name,
            region=region_name,
        )

    def _request(self, *, path: str, params: dict[str, str]) -> dict[str, object]:
        url = f"{KAKAO_LOCAL_BASE_URL}{path}?{urlencode(params)}"
        request = Request(url, headers={"Authorization": f"KakaoAK {self._rest_api_key}"})
        try:
            with urlopen(request, timeout=5) as response:  # noqa: S310
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            raise GeoProviderRequestError(
                f"Kakao Local request failed with HTTP {exc.code}.",
            ) from exc
        except URLError as exc:
            raise GeoProviderRequestError("Kakao Local request failed to connect.") from exc
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise GeoProviderRequestError("Kakao Local response was not valid JSON.") from exc
        if not isinstance(payload, dict):
            raise GeoProviderRequestError("Kakao Local response had an unexpected shape.")
        return payload


def _nullable_text(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _float_value(value: object) -> float | None:
    if isinstance(value, (int, float, str)):
        return float(value)
    return None


def _first_text(payload: dict[str, object], keys: tuple[str, ...], *, fallback: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback
