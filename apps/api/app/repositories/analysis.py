from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalysisRequest, AnalysisResult
from app.domain.payloads import CompetitorStorePayload, RawMetrics, ReportPayloadData


def create_analysis_request(
    session: Session,
    *,
    area_id: str,
    category_id: str,
    radius_m: int,
    data_mode: str,
    selected_boundary_id: str | None,
    input_snapshot: dict[str, object],
) -> AnalysisRequest:
    request = AnalysisRequest(
        area_id=area_id,
        category_id=category_id,
        radius_m=radius_m,
        data_mode=data_mode,
        selected_boundary_id=selected_boundary_id,
        input_snapshot=input_snapshot,
    )
    session.add(request)
    session.flush()
    return request


def create_analysis_result(
    session: Session,
    *,
    analysis_request_id: str,
    scores: dict[str, int],
    raw_metrics: RawMetrics,
    positive_factors: list[str],
    risk_factors: list[str],
    competitor_stores: list[CompetitorStorePayload],
    report_payload: ReportPayloadData,
    data_mode: str,
    data_sources: list[dict[str, object]],
    recommendation_level: str,
    recommendation_reasons: list[str],
    warning_reasons: list[str],
    map_layers: list[dict[str, object]],
    methodology_version: str,
) -> AnalysisResult:
    result = AnalysisResult(
        analysis_request_id=analysis_request_id,
        overall_fit_score=scores["overall_fit_score"],
        competition_score=scores["competition_score"],
        demand_score=scores["demand_score"],
        land_use_score=scores["land_use_score"],
        churn_risk_score=scores["churn_risk_score"],
        stability_score=scores["stability_score"],
        accessibility_score=scores["accessibility_score"],
        data_mode=data_mode,
        data_sources=data_sources,
        recommendation_level=recommendation_level,
        recommendation_reasons=recommendation_reasons,
        warning_reasons=warning_reasons,
        map_layers=map_layers,
        methodology_version=methodology_version,
        raw_metrics=raw_metrics,
        positive_factors=positive_factors,
        risk_factors=risk_factors,
        competitor_stores=competitor_stores,
        report_payload=report_payload,
    )
    session.add(result)
    session.flush()
    return result


def get_analysis_result(
    session: Session,
    analysis_id: str,
) -> tuple[AnalysisRequest, AnalysisResult]:
    statement = (
        select(AnalysisRequest, AnalysisResult)
        .join(AnalysisResult, AnalysisResult.analysis_request_id == AnalysisRequest.id)
        .where(AnalysisResult.id == analysis_id)
        .limit(1)
    )
    row = session.execute(statement).one_or_none()
    if row is None:
        raise LookupError("analysis not found")
    return row[0], row[1]
