from __future__ import annotations

from app.domain.payloads import RawMetrics, ReportPayloadData


def build_factor_lists(
    raw_metrics: RawMetrics,
    scores: dict[str, int],
) -> tuple[list[str], list[str]]:
    positives: list[str] = []
    risks: list[str] = []

    if scores["demand_score"] >= 75:
        positives.append("유동 지표가 샘플 기준선보다 높아 기본 수요가 안정적으로 보입니다.")
    if scores["land_use_score"] >= 80:
        positives.append("용도지역 조건이 선택 업종과 비교적 잘 맞습니다.")
    if scores["churn_risk_score"] >= 65:
        positives.append("최근 개폐업 사이클이 상대적으로 안정적인 편입니다.")
    if scores["competition_score"] <= 45:
        risks.append("동종 또는 유사 업종 밀도가 높아 경쟁 강도가 큽니다.")
    if scores["land_use_score"] <= 40:
        risks.append("용도지역 적합성이 낮아 업종 운영 조건을 별도로 확인해야 합니다.")
    if scores["churn_risk_score"] <= 45:
        risks.append("폐업률 또는 생존율 지표가 보수적으로 해석될 필요가 있습니다.")
    if float(raw_metrics["foot_traffic_night_average_index"]) < 75:
        risks.append("야간 유동이 낮아 시간대별 수요 편차를 고려해야 합니다.")

    return positives[:3], risks[:3]


def summarize_overall_fit(overall_fit_score: int) -> str:
    if overall_fit_score >= 80:
        return "계산된 지표 기준으로 적합도가 높은 편입니다."
    if overall_fit_score >= 65:
        return "계산된 지표 기준으로 기회와 리스크가 함께 존재합니다."
    if overall_fit_score >= 50:
        return "수요 조건은 일부 있으나 경쟁과 리스크를 함께 점검해야 합니다."
    return "현재 mock 지표 기준으로는 보수적으로 검토하는 편이 적절합니다."


def build_report_payload(
    *,
    area_name: str,
    category_name: str,
    radius_m: int,
    raw_metrics: RawMetrics,
    scores: dict[str, int],
    data_label: str,
) -> ReportPayloadData:
    positive_factors, risk_factors = build_factor_lists(raw_metrics, scores)
    summary = (
        f"{area_name}에서 {category_name} 업종을 {radius_m}m 반경으로 분석한 결과, "
        f"{summarize_overall_fit(scores['overall_fit_score'])}"
    )
    disclaimer = (
        f"이 결과는 {data_label} 기반 참고용 분석이며 "
        "창업 성공, 매출, 투자 성과를 보장하지 않습니다."
    )
    return {
        "summary": summary,
        "positive_factors": positive_factors,
        "risk_factors": risk_factors,
        "metric_evidence": raw_metrics,
        "disclaimers": [disclaimer],
        "llm_ready_payload": {
            "area_name": area_name,
            "category_name": category_name,
            "radius_m": radius_m,
            "scores": scores,
            "raw_metrics": raw_metrics,
            "positive_factors": positive_factors,
            "risk_factors": risk_factors,
            "instructions": [
                "raw_metrics에 없는 사실을 추가하지 않는다.",
                "창업 성공, 매출, 투자 결과를 단정하지 않는다.",
                "면책 문구를 유지한다.",
            ],
        },
    }
