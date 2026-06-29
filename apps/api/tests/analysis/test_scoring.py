from app.analysis.scoring import build_scores


def test_build_scores_returns_explainable_breakdown() -> None:
    raw_metrics = {
        "same_category_count_300m": 2,
        "same_category_count_500m": 3,
        "same_category_count_1000m": 5,
        "similar_category_count_300m": 1,
        "similar_category_count_500m": 2,
        "similar_category_count_1000m": 4,
        "district_same_category_count": 12,
        "franchise_store_count": 2,
        "competition_density_index": 4.0,
        "foot_traffic_daily_average_index": 118.2,
        "foot_traffic_weekend_average_index": 132.0,
        "foot_traffic_daytime_average_index": 116.0,
        "estimated_sales_amount": 182000000,
        "estimated_sales_count": 12450,
        "weekday_sales_ratio": 0.58,
        "daytime_sales_ratio": 0.73,
        "open_rate_12m": 0.21,
        "close_rate_12m": 0.14,
        "survival_rate_12m": 0.73,
        "avg_operation_months": 28.4,
        "stability_score_raw": 68,
        "land_use_fitness": "preferred",
    }

    scores = build_scores(raw_metrics)

    assert set(scores) == {
        "overall_fit_score",
        "competition_score",
        "demand_score",
        "land_use_score",
        "churn_risk_score",
        "stability_score",
        "accessibility_score",
    }
    assert all(0 <= value <= 100 for value in scores.values())
    assert scores["land_use_score"] == 90
    assert scores["competition_score"] >= 70
    assert scores["demand_score"] >= 70
    assert scores["overall_fit_score"] >= 60
