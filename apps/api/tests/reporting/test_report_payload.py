from app.reporting.report_payload import build_report_payload


def test_build_report_payload_includes_disclaimer_and_metric_facts_only() -> None:
    raw_metrics = {
        "same_category_count_300m": 2,
        "same_category_count_500m": 3,
        "same_category_count_1000m": 5,
        "similar_category_count_300m": 1,
        "similar_category_count_500m": 2,
        "similar_category_count_1000m": 4,
        "competition_density_index": 4.0,
        "foot_traffic_daily_average_index": 118.2,
        "foot_traffic_weekday_average_index": 109.0,
        "foot_traffic_weekend_average_index": 132.0,
        "foot_traffic_daytime_average_index": 116.0,
        "foot_traffic_night_average_index": 88.0,
        "open_rate_12m": 0.21,
        "close_rate_12m": 0.14,
        "survival_rate_12m": 0.73,
        "land_use_zone_name": "준주거지역",
        "land_use_fitness": "preferred",
    }
    scores = {
        "overall_fit_score": 76,
        "competition_score": 75,
        "demand_score": 76,
        "land_use_score": 90,
        "churn_risk_score": 67,
    }

    payload = build_report_payload(
        area_name="성수1가1동",
        category_name="카페",
        radius_m=500,
        raw_metrics=raw_metrics,
        scores=scores,
        data_label="mock sample data",
    )

    assert "창업 성공" in payload["disclaimers"][0]
    assert payload["llm_ready_payload"]["raw_metrics"] == raw_metrics
    assert payload["positive_factors"]

