from app.analysis.scoring import build_scores


def test_build_scores_returns_explainable_breakdown() -> None:
    raw_metrics = {
        "same_category_count_300m": 2,
        "same_category_count_500m": 3,
        "same_category_count_1000m": 5,
        "similar_category_count_300m": 1,
        "similar_category_count_500m": 2,
        "similar_category_count_1000m": 4,
        "competition_density_index": 4.0,
        "foot_traffic_daily_average_index": 118.2,
        "foot_traffic_weekend_average_index": 132.0,
        "close_rate_12m": 0.14,
        "survival_rate_12m": 0.73,
        "land_use_fitness": "preferred",
    }

    scores = build_scores(raw_metrics)

    assert scores["competition_score"] == 78
    assert scores["demand_score"] == 76
    assert scores["land_use_score"] == 90
    assert scores["churn_risk_score"] == 66
    assert scores["overall_fit_score"] == 77
