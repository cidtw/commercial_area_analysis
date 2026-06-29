from __future__ import annotations

from app.domain.payloads import RawMetrics


def as_float(raw_metrics: RawMetrics, key: str, default: float = 0.0) -> float:
    value = raw_metrics.get(key, default)
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float, str)):
        return float(value)
    return default


def build_recommendation(
    *,
    scores: dict[str, int],
    raw_metrics: RawMetrics,
) -> tuple[str, list[str], list[str]]:
    overall = scores["overall_fit_score"]
    competition = scores["competition_score"]
    demand = scores["demand_score"]
    land_use = scores["land_use_score"]
    stability = scores["stability_score"]
    accessibility = scores["accessibility_score"]

    if overall >= 78 and competition >= 55 and land_use >= 60:
        level = "recommended"
    elif overall >= 64:
        level = "conditional"
    elif overall >= 48:
        level = "caution"
    else:
        level = "not_recommended"

    same_500m = int(as_float(raw_metrics, "same_category_count_500m"))
    daily_index = round(as_float(raw_metrics, "foot_traffic_daily_average_index"), 1)
    land_use_name = str(raw_metrics.get("land_use_zone_name", "정보 없음"))
    close_rate = round(as_float(raw_metrics, "close_rate_12m") * 100, 1)
    stability_raw = round(as_float(raw_metrics, "stability_score_raw"), 1)
    sales_amount = int(as_float(raw_metrics, "estimated_sales_amount"))

    reasons: list[str] = []
    warnings: list[str] = []

    if demand >= 65:
        reasons.append(f"일평균 유동지수 {daily_index}와 수요 점수 {demand}점이 확인됩니다.")
    if competition >= 55:
        reasons.append(
            f"500m 반경 동종 업소 {same_500m}개 수준으로 "
            f"경쟁 점수 {competition}점을 확보했습니다.",
        )
    if land_use >= 65:
        reasons.append(f"용도지역 '{land_use_name}' 기준으로 업종 적합성이 {land_use}점입니다.")
    if stability >= 60:
        reasons.append(
            f"상권 안정성 raw 지표 {stability_raw}와 "
            f"안정성 점수 {stability}점이 확인됩니다.",
        )
    if accessibility >= 60 and sales_amount > 0:
        reasons.append(
            f"추정 매출 {sales_amount:,}원과 접근성 점수 "
            f"{accessibility}점이 수요 근거로 작동합니다.",
        )

    if competition <= 45:
        warnings.append(
            f"500m 반경 동종 업소 {same_500m}개로 "
            f"경쟁 점수는 {competition}점에 머뭅니다.",
        )
    if close_rate >= 18:
        warnings.append(f"최근 12개월 폐업률 {close_rate}%로 개폐업 리스크 점검이 필요합니다.")
    if land_use <= 45:
        warnings.append(f"용도지역 '{land_use_name}'은 업종 적합성이 낮아 별도 확인이 필요합니다.")
    if stability <= 45:
        warnings.append(f"상권 안정성 점수 {stability}점으로 변동성에 주의해야 합니다.")

    return level, reasons[:3], warnings[:3]
