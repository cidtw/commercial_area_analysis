from __future__ import annotations

import json
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.sources.sample_sources import (
    BoundarySampleSource,
    SeoulCompetitionSampleSource,
    SeoulSalesSampleSource,
    SeoulStabilitySampleSource,
    SobaStoreSampleSource,
)
from app.bootstrap.mock_seed import ensure_mock_seeded
from app.db.models import (
    Area,
    BusinessCategory,
    DistrictCompetitionStat,
    DistrictSalesStat,
    DistrictStabilityStat,
    Store,
)

BOUNDARY_DATASET_ID = "boundary-seongsu-sample"
COMPETITION_DATASET_ID = "seoul-competition-seongsu-sample"
SALES_DATASET_ID = "seoul-sales-seongsu-sample"
STABILITY_DATASET_ID = "seoul-stability-seongsu-sample"
STORE_DATASET_ID = "soba-store-seongsu-sample"


def build_lookup(rows: Iterable[tuple[str, str]]) -> dict[str, str]:
    return dict(rows)


def require_lookup(mapping: dict[str, str], code: str, *, entity_name: str) -> str:
    value = mapping.get(code)
    if value is None:
        raise LookupError(f"missing {entity_name} for code={code}")
    return value


def sync_sample_boundaries(session: Session, *, area_by_code: dict[str, str]) -> None:
    source = BoundarySampleSource()
    descriptor = source.describe()
    for record in source.load_boundaries():
        area_id = require_lookup(area_by_code, record.area_code, entity_name="area")
        area = session.get(Area, area_id)
        if area is None:
            raise LookupError(f"missing area row for code={record.area_code}")
        area.boundary_geojson = record.geometry
        area.boundary_geom = json.dumps(record.geometry, ensure_ascii=False)
        area.data_mode = descriptor.data_mode
        area.reference_date = descriptor.reference_date
        area.dataset_id = BOUNDARY_DATASET_ID
        area.is_mock = False
        area.source_name = descriptor.source_name
        area.source_version = descriptor.source_version


def sync_sample_stores(
    session: Session,
    *,
    area_by_code: dict[str, str],
    category_by_code: dict[str, str],
) -> None:
    source = SobaStoreSampleSource()
    descriptor = source.describe()
    for record in source.load_store_points():
        session.merge(
            Store(
                id=f"sample-store-{record.external_store_id}",
                name=record.name,
                category_id=require_lookup(
                    category_by_code,
                    record.category_code,
                    entity_name="category",
                ),
                area_id=require_lookup(area_by_code, record.area_code, entity_name="area"),
                address=record.address,
                latitude=record.latitude,
                longitude=record.longitude,
                point_geom=f"POINT({record.longitude} {record.latitude})",
                status="open",
                opened_on=None,
                closed_on=None,
                data_mode=descriptor.data_mode,
                reference_date=descriptor.reference_date,
                dataset_id=STORE_DATASET_ID,
                external_store_id=record.external_store_id,
                is_mock=False,
                source_name=descriptor.source_name,
                source_version=descriptor.source_version,
            ),
        )


def sync_sample_competition_stats(
    session: Session,
    *,
    area_by_code: dict[str, str],
    category_by_code: dict[str, str],
) -> None:
    source = SeoulCompetitionSampleSource()
    descriptor = source.describe()
    for record in source.load_competition_stats():
        session.merge(
            DistrictCompetitionStat(
                id=(
                    "sample-competition-"
                    f"{record.area_code}-{record.category_code}-{record.snapshot_month.isoformat()}"
                ),
                area_id=require_lookup(area_by_code, record.area_code, entity_name="area"),
                category_id=require_lookup(
                    category_by_code,
                    record.category_code,
                    entity_name="category",
                ),
                snapshot_month=record.snapshot_month,
                same_category_count=record.same_category_count,
                similar_category_count=record.similar_category_count,
                franchise_store_count=record.franchise_store_count,
                opened_rate_12m=record.opened_rate_12m,
                closed_rate_12m=record.closed_rate_12m,
                data_mode=descriptor.data_mode,
                dataset_id=COMPETITION_DATASET_ID,
            ),
        )


def sync_sample_stability_stats(
    session: Session,
    *,
    area_by_code: dict[str, str],
    category_by_code: dict[str, str],
) -> None:
    source = SeoulStabilitySampleSource()
    descriptor = source.describe()
    for record in source.load_stability_stats():
        session.merge(
            DistrictStabilityStat(
                id=(
                    "sample-stability-"
                    f"{record.area_code}-{record.category_code}-{record.snapshot_month.isoformat()}"
                ),
                area_id=require_lookup(area_by_code, record.area_code, entity_name="area"),
                category_id=require_lookup(
                    category_by_code,
                    record.category_code,
                    entity_name="category",
                ),
                snapshot_month=record.snapshot_month,
                avg_operation_months=record.avg_operation_months,
                avg_closed_operation_months=record.avg_closed_operation_months,
                change_index_code=record.change_index_code,
                change_index_label=record.change_index_label,
                stability_score_raw=record.stability_score_raw,
                data_mode=descriptor.data_mode,
                dataset_id=STABILITY_DATASET_ID,
            ),
        )


def sync_sample_sales_stats(
    session: Session,
    *,
    area_by_code: dict[str, str],
    category_by_code: dict[str, str],
) -> None:
    source = SeoulSalesSampleSource()
    descriptor = source.describe()
    for record in source.load_sales_stats():
        session.merge(
            DistrictSalesStat(
                id=(
                    "sample-sales-"
                    f"{record.area_code}-{record.category_code}-{record.snapshot_month.isoformat()}"
                ),
                area_id=require_lookup(area_by_code, record.area_code, entity_name="area"),
                category_id=require_lookup(
                    category_by_code,
                    record.category_code,
                    entity_name="category",
                ),
                snapshot_month=record.snapshot_month,
                estimated_sales_amount=record.estimated_sales_amount,
                estimated_sales_count=record.estimated_sales_count,
                weekday_sales_ratio=record.weekday_sales_ratio,
                weekend_sales_ratio=record.weekend_sales_ratio,
                daytime_sales_ratio=record.daytime_sales_ratio,
                night_sales_ratio=record.night_sales_ratio,
                target_customer_hint=record.target_customer_hint,
                data_mode=descriptor.data_mode,
                dataset_id=SALES_DATASET_ID,
            ),
        )


def seed_phase2_sample_data(session: Session) -> None:
    ensure_mock_seeded(session)
    area_by_code = build_lookup(session.execute(select(Area.code, Area.id)).tuples().all())
    category_by_code = build_lookup(
        session.execute(select(BusinessCategory.code, BusinessCategory.id)).tuples().all(),
    )

    sync_sample_boundaries(session, area_by_code=area_by_code)
    sync_sample_stores(session, area_by_code=area_by_code, category_by_code=category_by_code)
    sync_sample_competition_stats(
        session,
        area_by_code=area_by_code,
        category_by_code=category_by_code,
    )
    sync_sample_stability_stats(
        session,
        area_by_code=area_by_code,
        category_by_code=category_by_code,
    )
    sync_sample_sales_stats(session, area_by_code=area_by_code, category_by_code=category_by_code)
    session.commit()
