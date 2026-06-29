from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from app.adapters.sources.base import (
    BoundaryFeatureSourceRecord,
    CompetitionStatSourceRecord,
    DatasetDescriptor,
    SalesStatSourceRecord,
    StabilityStatSourceRecord,
    StorePointSourceRecord,
)

DATA_ROOT = Path(__file__).resolve().parent.parent / "sample_data"
SAMPLE_REFERENCE_DATE = date(2026, 6, 1)
SAMPLE_LICENSE_NOTE = "sample subset derived for local verification only"


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class SobaStoreSampleSource:
    def describe(self) -> DatasetDescriptor:
        return DatasetDescriptor(
            source_key="soba_store_source",
            source_name="소상공인시장진흥공단 상가정보 sample subset",
            source_version="2026.06-sample",
            reference_date=SAMPLE_REFERENCE_DATE,
            license_note=SAMPLE_LICENSE_NOTE,
            data_mode="sample",
        )

    def load_store_points(self, *, area_code: str | None = None) -> list[StorePointSourceRecord]:
        rows = load_csv_rows(DATA_ROOT / "soba_stores_seongsu_sample.csv")
        records = [
            StorePointSourceRecord(
                external_store_id=row["external_store_id"],
                area_code=row["area_code"],
                category_code=row["category_code"],
                category_name=row["category_name"],
                name=row["store_name"],
                address=row["address"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                data_mode="sample",
            )
            for row in rows
        ]
        if area_code is None:
            return records
        return [record for record in records if record.area_code == area_code]


class SeoulCompetitionSampleSource:
    def describe(self) -> DatasetDescriptor:
        return DatasetDescriptor(
            source_key="seoul_competition_source",
            source_name="서울시 상권분석 점포/행정동 sample subset",
            source_version="2026.06-sample",
            reference_date=SAMPLE_REFERENCE_DATE,
            license_note=SAMPLE_LICENSE_NOTE,
            data_mode="sample",
        )

    def load_competition_stats(
        self,
        *,
        area_code: str | None = None,
    ) -> list[CompetitionStatSourceRecord]:
        rows = load_csv_rows(DATA_ROOT / "seoul_competition_seongsu_sample.csv")
        records = [
            CompetitionStatSourceRecord(
                area_code=row["area_code"],
                category_code=row["category_code"],
                snapshot_month=parse_date(row["snapshot_month"]),
                same_category_count=int(row["same_category_count"]),
                similar_category_count=int(row["similar_category_count"]),
                franchise_store_count=int(row["franchise_store_count"]),
                opened_rate_12m=float(row["opened_rate_12m"]),
                closed_rate_12m=float(row["closed_rate_12m"]),
                data_mode="sample",
            )
            for row in rows
        ]
        if area_code is None:
            return records
        return [record for record in records if record.area_code == area_code]


class SeoulStabilitySampleSource:
    def describe(self) -> DatasetDescriptor:
        return DatasetDescriptor(
            source_key="seoul_stability_source",
            source_name="서울시 상권변화지표 sample subset",
            source_version="2026.06-sample",
            reference_date=SAMPLE_REFERENCE_DATE,
            license_note=SAMPLE_LICENSE_NOTE,
            data_mode="sample",
        )

    def load_stability_stats(
        self,
        *,
        area_code: str | None = None,
    ) -> list[StabilityStatSourceRecord]:
        rows = load_csv_rows(DATA_ROOT / "seoul_stability_seongsu_sample.csv")
        records = [
            StabilityStatSourceRecord(
                area_code=row["area_code"],
                category_code=row["category_code"],
                snapshot_month=parse_date(row["snapshot_month"]),
                avg_operation_months=float(row["avg_operation_months"]),
                avg_closed_operation_months=float(row["avg_closed_operation_months"]),
                change_index_code=row["change_index_code"],
                change_index_label=row["change_index_label"],
                stability_score_raw=float(row["stability_score_raw"]),
                data_mode="sample",
            )
            for row in rows
        ]
        if area_code is None:
            return records
        return [record for record in records if record.area_code == area_code]


class SeoulSalesSampleSource:
    def describe(self) -> DatasetDescriptor:
        return DatasetDescriptor(
            source_key="seoul_sales_source",
            source_name="서울시 추정매출 sample subset",
            source_version="2026.06-sample",
            reference_date=SAMPLE_REFERENCE_DATE,
            license_note=SAMPLE_LICENSE_NOTE,
            data_mode="sample",
        )

    def load_sales_stats(
        self,
        *,
        area_code: str | None = None,
    ) -> list[SalesStatSourceRecord]:
        rows = load_csv_rows(DATA_ROOT / "seoul_sales_seongsu_sample.csv")
        records = [
            SalesStatSourceRecord(
                area_code=row["area_code"],
                category_code=row["category_code"],
                snapshot_month=parse_date(row["snapshot_month"]),
                estimated_sales_amount=float(row["estimated_sales_amount"]),
                estimated_sales_count=int(row["estimated_sales_count"]),
                weekday_sales_ratio=float(row["weekday_sales_ratio"]),
                weekend_sales_ratio=float(row["weekend_sales_ratio"]),
                daytime_sales_ratio=float(row["daytime_sales_ratio"]),
                night_sales_ratio=float(row["night_sales_ratio"]),
                target_customer_hint=row["target_customer_hint"],
                data_mode="sample",
            )
            for row in rows
        ]
        if area_code is None:
            return records
        return [record for record in records if record.area_code == area_code]


class BoundarySampleSource:
    def describe(self) -> DatasetDescriptor:
        return DatasetDescriptor(
            source_key="boundary_source",
            source_name="행정동 경계 GeoJSON sample subset",
            source_version="2026.06-sample",
            reference_date=SAMPLE_REFERENCE_DATE,
            license_note=SAMPLE_LICENSE_NOTE,
            data_mode="sample",
        )

    def load_boundaries(
        self,
        *,
        area_code: str | None = None,
    ) -> list[BoundaryFeatureSourceRecord]:
        path = DATA_ROOT / "seongsu_boundaries.geojson"
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        features = payload["features"]
        records = [
            BoundaryFeatureSourceRecord(
                boundary_id=str(feature["properties"]["boundary_id"]),
                area_code=str(feature["properties"]["area_code"]),
                boundary_name=str(feature["properties"]["boundary_name"]),
                geometry=feature["geometry"],
                data_mode="sample",
            )
            for feature in features
        ]
        if area_code is None:
            return records
        return [record for record in records if record.area_code == area_code]
