from __future__ import annotations

from collections.abc import Sequence

METHODLOGY_DATA_MODES: Sequence[str] = ("mock", "sample")
METHODOLOGY_VERSION = "phase2-v1"

SCORE_FORMULAE: Sequence[dict[str, object]] = (
    {
        "score_key": "competition_score",
        "title": "경쟁 강도",
        "formula": "동종/유사 업종 밀도와 가맹점 수가 낮을수록 가산",
        "inputs": [
            "same_category_count_300m",
            "district_same_category_count",
            "district_similar_category_count",
            "franchise_store_count",
        ],
    },
    {
        "score_key": "demand_score",
        "title": "수요",
        "formula": "유동 지표와 추정 매출/건수를 함께 반영",
        "inputs": [
            "foot_traffic_daily_average_index",
            "foot_traffic_weekend_average_index",
            "estimated_sales_amount",
            "estimated_sales_count",
        ],
    },
    {
        "score_key": "land_use_score",
        "title": "용도 적합성",
        "formula": "용도지역 적합성 preferred/conditional/discouraged를 점수화",
        "inputs": ["land_use_fitness", "land_use_zone_name"],
    },
    {
        "score_key": "churn_risk_score",
        "title": "개폐업 리스크",
        "formula": "폐업률이 낮고 생존율이 높을수록 가산",
        "inputs": ["open_rate_12m", "close_rate_12m", "survival_rate_12m"],
    },
    {
        "score_key": "stability_score",
        "title": "안정성",
        "formula": "평균 영업 개월수와 상권변화지표 raw score를 결합",
        "inputs": ["avg_operation_months", "stability_score_raw", "change_index_label"],
    },
    {
        "score_key": "accessibility_score",
        "title": "접근성",
        "formula": "주중/주말·주간 수요 분포와 거래량 힌트를 반영",
        "inputs": [
            "foot_traffic_daytime_average_index",
            "weekday_sales_ratio",
            "daytime_sales_ratio",
            "estimated_sales_count",
        ],
    },
    {
        "score_key": "overall_fit_score",
        "title": "종합 적합도",
        "formula": "설명 가능한 6개 세부 점수의 가중 평균",
        "inputs": [
            "competition_score",
            "demand_score",
            "land_use_score",
            "churn_risk_score",
            "stability_score",
            "accessibility_score",
        ],
    },
)

METHODOLOGY_DISCLAIMER = (
    "이 분석은 계산된 지표를 설명하는 참고용 결과이며 "
    "창업 성공, 매출, 투자 성과를 보장하지 않습니다."
)
