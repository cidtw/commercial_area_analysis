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


@dataclass(frozen=True, slots=True)
class DistrictCompetitionRecord:
    area_id: str
    category_id: str
    same_category_count: int
    similar_category_count: int
    franchise_store_count: int
    opened_rate_12m: float
    closed_rate_12m: float


@dataclass(frozen=True, slots=True)
class DistrictStabilityRecord:
    area_id: str
    category_id: str
    avg_operation_months: float
    avg_closed_operation_months: float
    change_index_code: str
    change_index_label: str
    stability_score_raw: float


@dataclass(frozen=True, slots=True)
class DistrictSalesRecord:
    area_id: str
    category_id: str
    estimated_sales_amount: float
    estimated_sales_count: int
    weekday_sales_ratio: float
    weekend_sales_ratio: float
    daytime_sales_ratio: float
    night_sales_ratio: float
    target_customer_hint: str
