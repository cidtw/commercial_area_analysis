from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class AreaRecord:
    id: str
    code: str
    name: str
    district_name: str
    center_latitude: float
    center_longitude: float
    is_mock: bool


@dataclass(frozen=True, slots=True)
class CategoryRecord:
    id: str
    code: str
    name: str
    group_name: str
    similarity_group: str


@dataclass(frozen=True, slots=True)
class StoreRecord:
    id: str
    name: str
    category_id: str
    category_code: str
    category_name: str
    group_name: str
    similarity_group: str
    address: str
    latitude: float
    longitude: float
    status: str
    opened_on: date | None
    is_mock: bool


@dataclass(frozen=True, slots=True)
class FootTrafficRecord:
    area_id: str
    radius_m: int
    daily_average_index: float
    weekday_average_index: float
    weekend_average_index: float
    daytime_average_index: float
    night_average_index: float


@dataclass(frozen=True, slots=True)
class LandUseRecord:
    zone_name: str
    permitted_category_groups: tuple[str, ...]
    restriction_notes: str
    polygon_points: tuple[tuple[float, float], ...]


@dataclass(frozen=True, slots=True)
class OpenCloseRecord:
    area_id: str
    category_id: str
    opened_count_6m: int
    closed_count_6m: int
    opened_count_12m: int
    closed_count_12m: int
    survival_rate_12m: float

