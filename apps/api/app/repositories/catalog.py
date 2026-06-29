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
    DistrictCompetitionStat,
    DistrictSalesStat,
    DistrictStabilityStat,
    FootTrafficSnapshot,
    LandUseZone,
    OpenCloseStat,
    Store,
)
from app.analysis.geometry import haversine_distance_meters, point_in_polygon
from app.domain.records import (
    AreaRecord,
    CategoryRecord,
    DistrictCompetitionRecord,
    DistrictSalesRecord,
    DistrictStabilityRecord,
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


def find_area_for_point(
    session: Session,
    *,
    latitude: float,
    longitude: float,
) -> Area | None:
    areas = list_areas(session)
    for area in areas:
        coordinates = area.boundary_geojson.get("coordinates", []) if area.boundary_geojson else []
        if (
            isinstance(coordinates, list)
            and coordinates
            and isinstance(coordinates[0], list)
            and coordinates[0]
            and isinstance(coordinates[0][0], list)
        ):
            polygon = tuple(
                (float(point[0]), float(point[1]))
                for point in coordinates[0][0]
                if isinstance(point, list) and len(point) == 2
            )
            if polygon and point_in_polygon(latitude, longitude, polygon):
                return area
    ranked = sorted(
        areas,
        key=lambda area: haversine_distance_meters(
            latitude,
            longitude,
            area.center_latitude,
            area.center_longitude,
        ),
    )
    return ranked[0] if ranked else None


def get_category(session: Session, category_id: str) -> BusinessCategory:
    category = session.get(BusinessCategory, category_id)
    if category is None:
        raise LookupError("category not found")
    return category


def get_stores_with_categories(
    session: Session,
    *,
    data_mode: str | None = None,
) -> Sequence[tuple[Store, BusinessCategory]]:
    statement = (
        select(Store, BusinessCategory)
        .join(BusinessCategory, Store.category_id == BusinessCategory.id)
        .where(Store.status == "open")
        .order_by(Store.name)
    )
    if data_mode is not None:
        statement = statement.where(Store.data_mode == data_mode)
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
    data_mode: str,
) -> Sequence[tuple[Store, BusinessCategory]]:
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        statement = build_store_radius_statement(area=area, radius_m=radius_m).where(
            Store.data_mode == data_mode,
        )
        return [(store, category) for store, category in session.execute(statement)]
    return get_stores_with_categories_for_point(
        session,
        latitude=area.center_latitude,
        longitude=area.center_longitude,
        radius_m=radius_m,
        data_mode=data_mode,
    )


def get_stores_with_categories_for_point(
    session: Session,
    *,
    latitude: float,
    longitude: float,
    radius_m: int,
    data_mode: str,
) -> Sequence[tuple[Store, BusinessCategory]]:
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        origin_point = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326,
        ).cast(Geography(geometry_type="POINT", srid=4326))
        statement = (
            select(Store, BusinessCategory)
            .join(BusinessCategory, Store.category_id == BusinessCategory.id)
            .where(Store.status == "open")
            .where(Store.data_mode == data_mode)
            .where(ST_DWithin(Store.point_geom, origin_point, radius_m))
            .order_by(Store.name)
        )
        return [(store, category) for store, category in session.execute(statement)]

    latitude_delta = radius_m / 111_000
    longitude_delta = radius_m / 111_000
    statement = (
        select(Store, BusinessCategory)
        .join(BusinessCategory, Store.category_id == BusinessCategory.id)
        .where(Store.status == "open")
        .where(Store.data_mode == data_mode)
        .where(Store.latitude.between(latitude - latitude_delta, latitude + latitude_delta))
        .where(Store.longitude.between(longitude - longitude_delta, longitude + longitude_delta))
        .order_by(Store.name)
    )
    rows = [(store, category) for store, category in session.execute(statement)]
    return [
        (store, category)
        for store, category in rows
        if haversine_distance_meters(latitude, longitude, store.latitude, store.longitude) <= radius_m
    ]


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


def get_district_competition_stat(
    session: Session,
    area_id: str,
    category_id: str,
) -> DistrictCompetitionStat | None:
    statement = (
        select(DistrictCompetitionStat)
        .where(
            DistrictCompetitionStat.area_id == area_id,
            DistrictCompetitionStat.category_id == category_id,
        )
        .limit(1)
    )
    return session.scalar(statement)


def get_district_stability_stat(
    session: Session,
    area_id: str,
    category_id: str,
) -> DistrictStabilityStat | None:
    statement = (
        select(DistrictStabilityStat)
        .where(
            DistrictStabilityStat.area_id == area_id,
            DistrictStabilityStat.category_id == category_id,
        )
        .limit(1)
    )
    return session.scalar(statement)


def get_district_sales_stat(
    session: Session,
    area_id: str,
    category_id: str,
) -> DistrictSalesStat | None:
    statement = (
        select(DistrictSalesStat)
        .where(
            DistrictSalesStat.area_id == area_id,
            DistrictSalesStat.category_id == category_id,
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
        administrative_dong_name=area.administrative_dong_name,
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


def to_district_competition_record(
    stat: DistrictCompetitionStat | None,
) -> DistrictCompetitionRecord | None:
    if stat is None:
        return None
    return DistrictCompetitionRecord(
        area_id=stat.area_id,
        category_id=stat.category_id,
        same_category_count=stat.same_category_count,
        similar_category_count=stat.similar_category_count,
        franchise_store_count=stat.franchise_store_count,
        opened_rate_12m=stat.opened_rate_12m,
        closed_rate_12m=stat.closed_rate_12m,
    )


def to_district_stability_record(
    stat: DistrictStabilityStat | None,
) -> DistrictStabilityRecord | None:
    if stat is None:
        return None
    return DistrictStabilityRecord(
        area_id=stat.area_id,
        category_id=stat.category_id,
        avg_operation_months=stat.avg_operation_months,
        avg_closed_operation_months=stat.avg_closed_operation_months,
        change_index_code=stat.change_index_code,
        change_index_label=stat.change_index_label,
        stability_score_raw=stat.stability_score_raw,
    )


def to_district_sales_record(
    stat: DistrictSalesStat | None,
) -> DistrictSalesRecord | None:
    if stat is None:
        return None
    return DistrictSalesRecord(
        area_id=stat.area_id,
        category_id=stat.category_id,
        estimated_sales_amount=stat.estimated_sales_amount,
        estimated_sales_count=stat.estimated_sales_count,
        weekday_sales_ratio=stat.weekday_sales_ratio,
        weekend_sales_ratio=stat.weekend_sales_ratio,
        daytime_sales_ratio=stat.daytime_sales_ratio,
        night_sales_ratio=stat.night_sales_ratio,
        target_customer_hint=stat.target_customer_hint,
    )
