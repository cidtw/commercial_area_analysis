from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GeoSearchType = Literal["address", "place", "region"]


class GeoSearchItemResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    source: str
    latitude: float
    longitude: float
    address: str | None = None
    region: str | None = None


class GeoSearchResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    query: str
    type: GeoSearchType
    items: list[GeoSearchItemResponse]


class GeoReverseResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    source: str
    latitude: float
    longitude: float
    address: str | None = None
    region: str | None = None


class GeoSearchQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    query: str = Field(min_length=1, max_length=120)
    search_type: GeoSearchType
