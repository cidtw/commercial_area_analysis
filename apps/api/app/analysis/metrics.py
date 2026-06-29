from __future__ import annotations

from app.analysis.geometry import haversine_distance_meters, point_in_polygon
from app.domain.payloads import CompetitorStorePayload, RawMetrics
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
    competition: DistrictCompetitionRecord | None = None,
    stability: DistrictStabilityRecord | None = None,
    sales: DistrictSalesRecord | None = None,
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
                    "latitude": store.latitude,
                    "longitude": store.longitude,
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
    district_same_category_count = (
        competition.same_category_count if competition else same_category_counts[500]
    )
    district_similar_category_count = (
        competition.similar_category_count if competition else similar_category_counts[500]
    )
    franchise_store_count = competition.franchise_store_count if competition else 0
    competition_density_index = district_same_category_count + 0.5 * district_similar_category_count
    estimated_sales_amount = sales.estimated_sales_amount if sales else 0.0
    estimated_sales_count = sales.estimated_sales_count if sales else 0
    weekday_sales_ratio = sales.weekday_sales_ratio if sales else 0.5
    weekend_sales_ratio = sales.weekend_sales_ratio if sales else 0.5
    daytime_sales_ratio = sales.daytime_sales_ratio if sales else 0.5
    night_sales_ratio = sales.night_sales_ratio if sales else 0.5
    avg_operation_months = stability.avg_operation_months if stability else 18.0
    avg_closed_operation_months = stability.avg_closed_operation_months if stability else 9.0
    change_index_code = stability.change_index_code if stability else "unknown"
    change_index_label = stability.change_index_label if stability else "정보 없음"
    stability_score_raw = stability.stability_score_raw if stability else 50.0

    raw_metrics: RawMetrics = {
        "same_category_count_300m": same_category_counts[300],
        "same_category_count_500m": same_category_counts[500],
        "same_category_count_1000m": same_category_counts[1000],
        "similar_category_count_300m": similar_category_counts[300],
        "similar_category_count_500m": similar_category_counts[500],
        "similar_category_count_1000m": similar_category_counts[1000],
        "district_same_category_count": district_same_category_count,
        "district_similar_category_count": district_similar_category_count,
        "franchise_store_count": franchise_store_count,
        "competition_density_index": competition_density_index,
        "foot_traffic_daily_average_index": traffic.daily_average_index if traffic else 90.0,
        "foot_traffic_weekday_average_index": traffic.weekday_average_index if traffic else 88.0,
        "foot_traffic_weekend_average_index": traffic.weekend_average_index if traffic else 92.0,
        "foot_traffic_daytime_average_index": traffic.daytime_average_index if traffic else 87.0,
        "foot_traffic_night_average_index": traffic.night_average_index if traffic else 85.0,
        "open_rate_12m": round(open_rate_12m, 4),
        "close_rate_12m": round(close_rate_12m, 4),
        "survival_rate_12m": round(survival_rate_12m, 4),
        "avg_operation_months": round(avg_operation_months, 1),
        "avg_closed_operation_months": round(avg_closed_operation_months, 1),
        "change_index_code": change_index_code,
        "change_index_label": change_index_label,
        "stability_score_raw": round(stability_score_raw, 1),
        "estimated_sales_amount": round(estimated_sales_amount, 2),
        "estimated_sales_count": estimated_sales_count,
        "weekday_sales_ratio": round(weekday_sales_ratio, 4),
        "weekend_sales_ratio": round(weekend_sales_ratio, 4),
        "daytime_sales_ratio": round(daytime_sales_ratio, 4),
        "night_sales_ratio": round(night_sales_ratio, 4),
        "target_customer_hint": sales.target_customer_hint if sales else "정보 없음",
        "land_use_zone_name": land_use_zone.zone_name if land_use_zone else "정보 없음",
        "land_use_fitness": normalize_land_use_fit(category.group_name, land_use_zone),
    }

    return raw_metrics, competitor_rows[:10]
