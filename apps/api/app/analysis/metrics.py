from __future__ import annotations

from app.analysis.geometry import haversine_distance_meters, point_in_polygon
from app.domain.payloads import CompetitorStorePayload, RawMetrics
from app.domain.records import (
    AreaRecord,
    CategoryRecord,
    FootTrafficRecord,
    LandUseRecord,
    OpenCloseRecord,
    StoreRecord,
)

DISTANCE_BUCKETS = (300, 500, 1000)


def clamp_rate(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def normalize_land_use_fit(category_group: str, zone: LandUseRecord | None) -> str:
    if zone is None:
        return "conditional"
    if category_group in zone.permitted_category_groups:
        return "preferred"
    if {"food_beverage", "retail"} & set(zone.permitted_category_groups):
        return "conditional"
    return "discouraged"


def build_metric_snapshot(
    *,
    area: AreaRecord,
    category: CategoryRecord,
    stores: list[StoreRecord],
    traffic: FootTrafficRecord | None,
    land_use_zones: list[LandUseRecord],
    open_close: OpenCloseRecord | None,
    selected_radius_m: int,
) -> tuple[RawMetrics, list[CompetitorStorePayload]]:
    same_category_counts = dict.fromkeys(DISTANCE_BUCKETS, 0)
    similar_category_counts = dict.fromkeys(DISTANCE_BUCKETS, 0)
    competitor_rows: list[CompetitorStorePayload] = []

    for store in stores:
        if store.status != "open":
            continue
        distance_m = haversine_distance_meters(
            area.center_latitude,
            area.center_longitude,
            store.latitude,
            store.longitude,
        )
        for bucket in DISTANCE_BUCKETS:
            if distance_m <= bucket:
                if store.category_id == category.id:
                    same_category_counts[bucket] += 1
                elif store.similarity_group == category.similarity_group:
                    similar_category_counts[bucket] += 1
        if distance_m <= selected_radius_m and (
            store.category_id == category.id or store.similarity_group == category.similarity_group
        ):
            competitor_rows.append(
                {
                    "id": store.id,
                    "name": store.name,
                    "category_name": store.category_name,
                    "distance_m": round(distance_m, 1),
                    "address": store.address,
                    "status": store.status,
                    "is_mock": store.is_mock,
                },
            )

    competitor_rows.sort(key=lambda item: float(item["distance_m"]))
    land_use_zone = next(
        (
            zone
            for zone in land_use_zones
            if point_in_polygon(
                area.center_latitude,
                area.center_longitude,
                zone.polygon_points,
            )
        ),
        land_use_zones[0] if land_use_zones else None,
    )

    current_supply_base = same_category_counts[1000]
    opened_count_12m = open_close.opened_count_12m if open_close else 0
    closed_count_12m = open_close.closed_count_12m if open_close else 0
    starting_supply_base = max(current_supply_base + closed_count_12m - opened_count_12m, 0)
    denominator = max(starting_supply_base + opened_count_12m, 1)
    open_rate_12m = clamp_rate(opened_count_12m / denominator)
    close_rate_12m = clamp_rate(closed_count_12m / denominator)
    survival_rate_12m = open_close.survival_rate_12m if open_close else 0.55

    raw_metrics: RawMetrics = {
        "same_category_count_300m": same_category_counts[300],
        "same_category_count_500m": same_category_counts[500],
        "same_category_count_1000m": same_category_counts[1000],
        "similar_category_count_300m": similar_category_counts[300],
        "similar_category_count_500m": similar_category_counts[500],
        "similar_category_count_1000m": similar_category_counts[1000],
        "competition_density_index": same_category_counts[500] + 0.5 * similar_category_counts[500],
        "foot_traffic_daily_average_index": traffic.daily_average_index if traffic else 90.0,
        "foot_traffic_weekday_average_index": traffic.weekday_average_index if traffic else 88.0,
        "foot_traffic_weekend_average_index": traffic.weekend_average_index if traffic else 92.0,
        "foot_traffic_daytime_average_index": traffic.daytime_average_index if traffic else 87.0,
        "foot_traffic_night_average_index": traffic.night_average_index if traffic else 85.0,
        "open_rate_12m": round(open_rate_12m, 4),
        "close_rate_12m": round(close_rate_12m, 4),
        "survival_rate_12m": round(survival_rate_12m, 4),
        "land_use_zone_name": land_use_zone.zone_name if land_use_zone else "정보 없음",
        "land_use_fitness": normalize_land_use_fit(category.group_name, land_use_zone),
    }

    return raw_metrics, competitor_rows[:10]
