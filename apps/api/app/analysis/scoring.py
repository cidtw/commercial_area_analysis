from __future__ import annotations


def clamp(value: float, minimum: float, maximum: float) -> float:
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def scale_up(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return clamp((value - low) / (high - low), 0.0, 1.0) * 100


def scale_down(value: float, low: float, high: float) -> float:
    return 100 - scale_up(value, low, high)


def land_use_score_for(label: str) -> int:
    match label:
        case "preferred":
            return 90
        case "conditional":
            return 65
        case "discouraged":
            return 30
        case _:
            return 50


def build_scores(raw_metrics: dict[str, float | int | str]) -> dict[str, int]:
    competition_density = float(raw_metrics["competition_density_index"])
    same_category_300m = float(raw_metrics["same_category_count_300m"])
    district_same_category = float(raw_metrics.get("district_same_category_count", 0))
    franchise_store_count = float(raw_metrics.get("franchise_store_count", 0))
    daily_index = float(raw_metrics["foot_traffic_daily_average_index"])
    weekend_index = float(raw_metrics["foot_traffic_weekend_average_index"])
    daytime_index = float(raw_metrics.get("foot_traffic_daytime_average_index", daily_index))
    close_rate = float(raw_metrics["close_rate_12m"])
    open_rate = float(raw_metrics.get("open_rate_12m", 0.15))
    survival_rate = float(raw_metrics["survival_rate_12m"])
    estimated_sales_amount = float(raw_metrics.get("estimated_sales_amount", 0))
    estimated_sales_count = float(raw_metrics.get("estimated_sales_count", 0))
    weekday_sales_ratio = float(raw_metrics.get("weekday_sales_ratio", 0.5))
    daytime_sales_ratio = float(raw_metrics.get("daytime_sales_ratio", 0.5))
    stability_score_raw = float(raw_metrics.get("stability_score_raw", 50))
    avg_operation_months = float(raw_metrics.get("avg_operation_months", 18))
    land_use_fitness = str(raw_metrics["land_use_fitness"])

    competition_score = round(
        0.4 * scale_down(competition_density, 0, 40)
        + 0.25 * scale_down(same_category_300m, 0, 8)
        + 0.2 * scale_down(district_same_category, 0, 40)
        + 0.15 * scale_down(franchise_store_count, 0, 12),
    )
    demand_score = round(
        0.35 * scale_up(daily_index, 60, 140)
        + 0.2 * scale_up(weekend_index, 60, 150)
        + 0.3 * scale_up(estimated_sales_amount, 60_000_000, 220_000_000)
        + 0.15 * scale_up(estimated_sales_count, 3_000, 15_000),
    )
    land_use_score = land_use_score_for(land_use_fitness)
    churn_risk_score = round(
        0.45 * scale_down(close_rate, 0.05, 0.35)
        + 0.35 * scale_up(survival_rate, 0.45, 0.9)
        + 0.2 * scale_down(open_rate, 0.05, 0.4),
    )
    stability_score = round(
        0.6 * scale_up(stability_score_raw, 40, 90)
        + 0.4 * scale_up(avg_operation_months, 12, 48),
    )
    accessibility_score = round(
        0.4 * scale_up(daytime_index, 60, 140)
        + 0.25 * scale_up(estimated_sales_count, 3_000, 15_000)
        + 0.2 * scale_up(weekday_sales_ratio, 0.45, 0.75)
        + 0.15 * scale_up(daytime_sales_ratio, 0.45, 0.8),
    )
    overall_fit_score = round(
        0.22 * competition_score
        + 0.22 * demand_score
        + 0.16 * land_use_score
        + 0.16 * churn_risk_score
        + 0.14 * stability_score
        + 0.10 * accessibility_score,
    )

    return {
        "overall_fit_score": overall_fit_score,
        "competition_score": competition_score,
        "demand_score": demand_score,
        "land_use_score": land_use_score,
        "churn_risk_score": churn_risk_score,
        "stability_score": stability_score,
        "accessibility_score": accessibility_score,
    }
