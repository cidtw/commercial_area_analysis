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
    daily_index = float(raw_metrics["foot_traffic_daily_average_index"])
    weekend_index = float(raw_metrics["foot_traffic_weekend_average_index"])
    close_rate = float(raw_metrics["close_rate_12m"])
    survival_rate = float(raw_metrics["survival_rate_12m"])
    land_use_fitness = str(raw_metrics["land_use_fitness"])

    competition_score = round(
        0.7 * scale_down(competition_density, 0, 20)
        + 0.3 * scale_down(same_category_300m, 0, 8),
    )
    demand_score = round(
        0.6 * scale_up(daily_index, 60, 140) + 0.4 * scale_up(weekend_index, 60, 150),
    )
    land_use_score = land_use_score_for(land_use_fitness)
    churn_risk_score = round(
        0.5 * scale_down(close_rate, 0.05, 0.35) + 0.5 * scale_up(survival_rate, 0.45, 0.9),
    )
    overall_fit_score = round(
        0.30 * competition_score
        + 0.30 * demand_score
        + 0.20 * land_use_score
        + 0.20 * churn_risk_score,
    )

    return {
        "overall_fit_score": overall_fit_score,
        "competition_score": competition_score,
        "demand_score": demand_score,
        "land_use_score": land_use_score,
        "churn_risk_score": churn_risk_score,
    }

