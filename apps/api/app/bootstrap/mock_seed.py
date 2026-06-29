from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.mock_source import MockSeedAdapter
from app.db.models import (
    Area,
    BusinessCategory,
    FootTrafficSnapshot,
    LandUseZone,
    OpenCloseStat,
    Store,
)

MOCK_REFERENCE_DATE = date(2026, 6, 1)
MOCK_DATASET_ID = "mock-seongsu-core"


def require_str(value: object) -> str:
    if isinstance(value, str):
        return value
    raise TypeError("expected string value in mock seed data")


def require_float(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise TypeError("expected numeric value in mock seed data")


def require_int(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    raise TypeError("expected integer value in mock seed data")


def require_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("expected string list in mock seed data")
    items: list[str] = []
    for item in value:
        items.append(require_str(item))
    return items


def optional_date_from_row(row: dict[str, object], key: str) -> date | None:
    value = row[key]
    if value is None:
        return None
    return parse_iso_date(require_str(value))


def parse_iso_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value)


def seed_database(session: Session) -> None:
    payload = MockSeedAdapter().load()
    for row in payload["areas"]:
        session.merge(
            Area(
                id=require_str(row["id"]),
                code=require_str(row["code"]),
                name=require_str(row["name"]),
                district_name=require_str(row["district_name"]),
                administrative_dong_name=require_str(row["administrative_dong_name"]),
                center_latitude=require_float(row["center_latitude"]),
                center_longitude=require_float(row["center_longitude"]),
                center_point=f"POINT({row['center_longitude']} {row['center_latitude']})",
                boundary_geojson=row["boundary_geojson"],
                boundary_geom=str(row["boundary_geojson"]),
                data_mode="mock",
                reference_date=MOCK_REFERENCE_DATE,
                dataset_id=MOCK_DATASET_ID,
                is_mock=bool(row["is_mock"]),
                source_name=require_str(row["source_name"]),
                source_version=require_str(row["source_version"]),
            ),
        )
    for row in payload["business_categories"]:
        session.merge(BusinessCategory(**row))
    for row in payload["stores"]:
        session.merge(
            Store(
                id=require_str(row["id"]),
                name=require_str(row["name"]),
                category_id=require_str(row["category_id"]),
                area_id=require_str(row["area_id"]),
                address=require_str(row["address"]),
                latitude=require_float(row["latitude"]),
                longitude=require_float(row["longitude"]),
                point_geom=f"POINT({row['longitude']} {row['latitude']})",
                status=require_str(row["status"]),
                opened_on=optional_date_from_row(row, "opened_on"),
                closed_on=optional_date_from_row(row, "closed_on"),
                data_mode="mock",
                reference_date=MOCK_REFERENCE_DATE,
                dataset_id=MOCK_DATASET_ID,
                is_mock=bool(row["is_mock"]),
                source_name=require_str(row["source_name"]),
                source_version=require_str(row["source_version"]),
            ),
        )
    for row in payload["foot_traffic"]:
        session.merge(
            FootTrafficSnapshot(
                id=require_str(row["id"]),
                area_id=require_str(row["area_id"]),
                snapshot_month=parse_iso_date(require_str(row["snapshot_month"])),
                radius_m=require_int(row["radius_m"]),
                daily_average_index=require_float(row["daily_average_index"]),
                weekday_average_index=require_float(row["weekday_average_index"]),
                weekend_average_index=require_float(row["weekend_average_index"]),
                daytime_average_index=require_float(row["daytime_average_index"]),
                night_average_index=require_float(row["night_average_index"]),
                data_mode="mock",
                reference_date=MOCK_REFERENCE_DATE,
                dataset_id=MOCK_DATASET_ID,
                is_mock=bool(row["is_mock"]),
            ),
        )
    for row in payload["land_use"]:
        session.merge(
            LandUseZone(
                id=require_str(row["id"]),
                area_id=require_str(row["area_id"]),
                zone_code=require_str(row["zone_code"]),
                zone_name=require_str(row["zone_name"]),
                permitted_category_groups=require_str_list(row["permitted_category_groups"]),
                restriction_notes=require_str(row["restriction_notes"]),
                boundary_geojson=row["boundary_geojson"],
                zone_geom=str(row["boundary_geojson"]),
                data_mode="mock",
                reference_date=MOCK_REFERENCE_DATE,
                dataset_id=MOCK_DATASET_ID,
                is_mock=bool(row["is_mock"]),
            ),
        )
    for row in payload["open_close_stats"]:
        session.merge(
            OpenCloseStat(
                id=require_str(row["id"]),
                area_id=require_str(row["area_id"]),
                category_id=require_str(row["category_id"]),
                snapshot_month=parse_iso_date(require_str(row["snapshot_month"])),
                opened_count_6m=require_int(row["opened_count_6m"]),
                closed_count_6m=require_int(row["closed_count_6m"]),
                opened_count_12m=require_int(row["opened_count_12m"]),
                closed_count_12m=require_int(row["closed_count_12m"]),
                survival_rate_12m=require_float(row["survival_rate_12m"]),
                data_mode="mock",
                reference_date=MOCK_REFERENCE_DATE,
                dataset_id=MOCK_DATASET_ID,
                is_mock=bool(row["is_mock"]),
            ),
        )
    session.commit()


def ensure_mock_seeded(session: Session) -> None:
    has_area = session.scalar(select(Area.id).limit(1))
    if has_area is None:
        seed_database(session)
