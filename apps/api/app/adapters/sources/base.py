from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal, Protocol

DataMode = Literal["mock", "sample", "real"]


@dataclass(frozen=True, slots=True)
class DatasetDescriptor:
    source_key: str
    source_name: str
    source_version: str
    reference_date: date
    license_note: str
    data_mode: DataMode


@dataclass(frozen=True, slots=True)
class StorePointSourceRecord:
    external_store_id: str
    area_code: str
    category_code: str
    category_name: str
    name: str
    address: str
    latitude: float
    longitude: float
    data_mode: DataMode


@dataclass(frozen=True, slots=True)
class CompetitionStatSourceRecord:
    area_code: str
    category_code: str
    snapshot_month: date
    same_category_count: int
    similar_category_count: int
    franchise_store_count: int
    opened_rate_12m: float
    closed_rate_12m: float
    data_mode: DataMode


@dataclass(frozen=True, slots=True)
class StabilityStatSourceRecord:
    area_code: str
    category_code: str
    snapshot_month: date
    avg_operation_months: float
    avg_closed_operation_months: float
    change_index_code: str
    change_index_label: str
    stability_score_raw: float
    data_mode: DataMode


@dataclass(frozen=True, slots=True)
class SalesStatSourceRecord:
    area_code: str
    category_code: str
    snapshot_month: date
    estimated_sales_amount: float
    estimated_sales_count: int
    weekday_sales_ratio: float
    weekend_sales_ratio: float
    daytime_sales_ratio: float
    night_sales_ratio: float
    target_customer_hint: str
    data_mode: DataMode


@dataclass(frozen=True, slots=True)
class BoundaryFeatureSourceRecord:
    boundary_id: str
    area_code: str
    boundary_name: str
    geometry: dict[str, object]
    data_mode: DataMode


class Phase2Source(Protocol):
    def describe(self) -> DatasetDescriptor:
        ...
