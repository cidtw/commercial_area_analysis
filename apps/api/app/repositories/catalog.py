from __future__ import annotations

from collections.abc import Sequence

from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import func

from app.db.models import (
    Area,
    BusinessCategory,
    FootTrafficSnapshot,
    LandUseZone,
    OpenCloseStat,
    Store,
)
from app.domain.records import (
    AreaRecord,
    CategoryRecord,
    FootTrafficRecord,
    LandUseRecord,
    OpenCloseRecord,
    StoreRecord,
)


def list_areas(session: Session) -> list[Area]:
    return list(session.scalars(select(Area).order_by(Area.name)))


def list_categories(session: Session) -> list[BusinessCategory]:
    return list(session.scalars(select(BusinessCategory).order_by(BusinessCategory.name)))


def get_area(session: Session, area_id: str) -> Area:
    area = session.get(Area, area_id)
    if area is None:
        raise LookupError("area not found")
    return area


def get_category(session: Session, category_id: str) -> BusinessCategory:
    category = session.get(BusinessCategory, category_id)
    if category is None:
        raise LookupError("category not found")
    return category


def get_stores_with_categories(session: Session) -> Sequence[tuple[Store, BusinessCategory]]:
    statement = (
        select(Store, BusinessCategory)
        .join(BusinessCategory, Store.category_id == BusinessCategory.id)
        .where(Store.status == "open")
        .order_by(Store.name)
    )
    return [(store, category) for store, category in session.execute(statement)]


def build_store_radius_statement(
    *,
    area: AreaRecord,
    radius_m: int,
) -> Select[tuple[Store, BusinessCategory]]:
    origin_point = func.ST_SetSRID(
        func.ST_MakePoint(area.center_longitude, area.center_latitude),
        4326,
    ).cast(Geography(geometry_type="POINT", srid=4326))
    return (
        select(Store, BusinessCategory)
        .join(BusinessCategory, Store.category_id == BusinessCategory.id)
        .where(Store.status == "open")
        .where(ST_DWithin(Store.point_geom, origin_point, radius_m))
        .order_by(Store.name)
    )


def get_stores_with_categories_for_analysis(
    session: Session,
    *,
    area: AreaRecord,
    radius_m: int,
) -> Sequence[tuple[Store, BusinessCategory]]:
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        statement = build_store_radius_statement(area=area, radius_m=radius_m)
        return [(store, category) for store, category in session.execute(statement)]
    return get_stores_with_categories(session)


def get_foot_traffic(session: Session, area_id: str, radius_m: int) -> FootTrafficSnapshot | None:
    statement = (
        select(FootTrafficSnapshot)
        .where(FootTrafficSnapshot.area_id == area_id, FootTrafficSnapshot.radius_m == radius_m)
        .limit(1)
    )
    return session.scalar(statement)


def get_land_use_zones(session: Session, area_id: str) -> list[LandUseZone]:
    statement = select(LandUseZone).where(
        (LandUseZone.area_id == area_id) | (LandUseZone.area_id.is_(None)),
    )
    return list(session.scalars(statement))


def get_open_close_stat(session: Session, area_id: str, category_id: str) -> OpenCloseStat | None:
    statement = (
        select(OpenCloseStat)
        .where(
            OpenCloseStat.area_id == area_id,
            OpenCloseStat.category_id == category_id,
        )
        .limit(1)
    )
    return session.scalar(statement)


def to_area_record(area: Area) -> AreaRecord:
    return AreaRecord(
        id=area.id,
        code=area.code,
        name=area.name,
        district_name=area.district_name,
        center_latitude=area.center_latitude,
        center_longitude=area.center_longitude,
        is_mock=area.is_mock,
    )


def to_category_record(category: BusinessCategory) -> CategoryRecord:
    return CategoryRecord(
        id=category.id,
        code=category.code,
        name=category.name,
        group_name=category.group_name,
        similarity_group=category.similarity_group,
    )


def to_store_records(rows: Sequence[tuple[Store, BusinessCategory]]) -> list[StoreRecord]:
    records: list[StoreRecord] = []
    for store, category in rows:
        records.append(
            StoreRecord(
                id=store.id,
                name=store.name,
                category_id=category.id,
                category_code=category.code,
                category_name=category.name,
                group_name=category.group_name,
                similarity_group=category.similarity_group,
                address=store.address,
                latitude=store.latitude,
                longitude=store.longitude,
                status=store.status,
                opened_on=store.opened_on,
                is_mock=store.is_mock,
            ),
        )
    return records


def to_foot_traffic_record(snapshot: FootTrafficSnapshot | None) -> FootTrafficRecord | None:
    if snapshot is None:
        return None
    return FootTrafficRecord(
        area_id=snapshot.area_id,
        radius_m=snapshot.radius_m,
        daily_average_index=snapshot.daily_average_index,
        weekday_average_index=snapshot.weekday_average_index,
        weekend_average_index=snapshot.weekend_average_index,
        daytime_average_index=snapshot.daytime_average_index,
        night_average_index=snapshot.night_average_index,
    )


def to_land_use_records(zones: list[LandUseZone]) -> list[LandUseRecord]:
    records: list[LandUseRecord] = []
    for zone in zones:
        coordinates = zone.boundary_geojson.get("coordinates", []) if zone.boundary_geojson else []
        polygon: list[tuple[float, float]] = []
        if isinstance(coordinates, list) and coordinates:
            first_polygon = coordinates[0]
            if isinstance(first_polygon, list) and first_polygon:
                first_ring = first_polygon[0]
                if isinstance(first_ring, list):
                    polygon = [
                        (float(point[0]), float(point[1]))
                        for point in first_ring
                        if isinstance(point, list) and len(point) == 2
                    ]
        records.append(
            LandUseRecord(
                zone_name=zone.zone_name,
                permitted_category_groups=tuple(
                    str(item) for item in zone.permitted_category_groups
                ),
                restriction_notes=zone.restriction_notes,
                polygon_points=tuple(polygon),
            ),
        )
    return records


def to_open_close_record(stat: OpenCloseStat | None) -> OpenCloseRecord | None:
    if stat is None:
        return None
    return OpenCloseRecord(
        area_id=stat.area_id,
        category_id=stat.category_id,
        opened_count_6m=stat.opened_count_6m,
        closed_count_6m=stat.closed_count_6m,
        opened_count_12m=stat.opened_count_12m,
        closed_count_12m=stat.closed_count_12m,
        survival_rate_12m=stat.survival_rate_12m,
    )
