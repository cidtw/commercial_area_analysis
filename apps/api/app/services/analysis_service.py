from __future__ import annotations

from collections.abc import Mapping, Sequence

from sqlalchemy.orm import Session

from app.analysis.metrics import build_metric_snapshot
from app.analysis.scoring import build_scores
from app.core.config import get_settings
from app.domain.payloads import CompetitorStorePayload, RawMetrics, ReportPayloadData
from app.reporting.report_payload import build_report_payload
from app.repositories import analysis as analysis_repository
from app.repositories import catalog as catalog_repository
from app.schemas.analysis import (
    AnalysisResponse,
    CompetitorStoreItem,
    ReportPayloadResponse,
    ScoreBreakdown,
)
from app.schemas.catalog import AreaSummary, CategorySummary


def normalize_raw_metrics(payload: Mapping[str, object]) -> RawMetrics:
    return {
        key: value if isinstance(value, (float, int, str)) else str(value)
        for key, value in payload.items()
    }


def normalize_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def normalize_mapping(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    return {}


def normalize_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float, str)):
        return int(value)
    return 0


def normalize_competitor_stores(
    payload: Sequence[Mapping[str, object]],
) -> list[CompetitorStorePayload]:
    return [
        CompetitorStorePayload(
            id=str(item["id"]),
            name=str(item["name"]),
            category_name=str(item["category_name"]),
            distance_m=(
                float(item["distance_m"])
                if isinstance(item["distance_m"], (float, int, str))
                else 0.0
            ),
            address=str(item["address"]),
            status=str(item["status"]),
            is_mock=bool(item["is_mock"]),
        )
        for item in payload
    ]


def normalize_report_payload(payload: Mapping[str, object]) -> ReportPayloadData:
    positive_factors = normalize_string_list(payload.get("positive_factors", []))
    risk_factors = normalize_string_list(payload.get("risk_factors", []))
    disclaimers = normalize_string_list(payload.get("disclaimers", []))
    llm_ready_payload = normalize_mapping(payload.get("llm_ready_payload", {}))
    score_mapping = normalize_mapping(llm_ready_payload.get("scores", {}))
    return ReportPayloadData(
        summary=str(payload.get("summary", "")),
        positive_factors=positive_factors,
        risk_factors=risk_factors,
        metric_evidence=normalize_raw_metrics(
            normalize_mapping(payload.get("metric_evidence", {}))
        ),
        disclaimers=disclaimers,
        llm_ready_payload={
            "area_name": str(llm_ready_payload.get("area_name", "")),
            "category_name": str(llm_ready_payload.get("category_name", "")),
            "radius_m": normalize_int(llm_ready_payload.get("radius_m", 0)),
            "scores": {
                key: normalize_int(value)
                for key, value in score_mapping.items()
                if isinstance(key, str)
            },
            "raw_metrics": normalize_raw_metrics(
                normalize_mapping(llm_ready_payload.get("raw_metrics", {}))
            ),
            "positive_factors": normalize_string_list(
                llm_ready_payload.get("positive_factors", [])
            ),
            "risk_factors": normalize_string_list(
                llm_ready_payload.get("risk_factors", [])
            ),
            "instructions": normalize_string_list(llm_ready_payload.get("instructions", [])),
        },
    )


def run_analysis(
    session: Session,
    *,
    area_id: str,
    category_id: str,
    radius_m: int,
) -> AnalysisResponse:
    settings = get_settings()
    area_model = catalog_repository.get_area(session, area_id)
    category_model = catalog_repository.get_category(session, category_id)
    area = catalog_repository.to_area_record(area_model)
    category = catalog_repository.to_category_record(category_model)
    stores = catalog_repository.to_store_records(
        catalog_repository.get_stores_with_categories_for_analysis(
            session,
            area=area,
            radius_m=1000,
        )
    )
    foot_traffic = catalog_repository.to_foot_traffic_record(
        catalog_repository.get_foot_traffic(session, area.id, radius_m),
    )
    land_use_zones = catalog_repository.to_land_use_records(
        catalog_repository.get_land_use_zones(session, area.id),
    )
    open_close = catalog_repository.to_open_close_record(
        catalog_repository.get_open_close_stat(session, area.id, category.id),
    )

    raw_metrics, competitor_rows = build_metric_snapshot(
        area=area,
        category=category,
        stores=stores,
        traffic=foot_traffic,
        land_use_zones=land_use_zones,
        open_close=open_close,
        selected_radius_m=radius_m,
    )
    scores = build_scores(raw_metrics)
    report_payload = build_report_payload(
        area_name=area.name,
        category_name=category.name,
        radius_m=radius_m,
        raw_metrics=raw_metrics,
        scores=scores,
        data_label=settings.mock_data_label,
    )
    request = analysis_repository.create_analysis_request(
        session,
        area_id=area.id,
        category_id=category.id,
        radius_m=radius_m,
        input_snapshot={
            "area_id": area.id,
            "category_id": category.id,
            "radius_m": radius_m,
        },
    )
    result = analysis_repository.create_analysis_result(
        session,
        analysis_request_id=request.id,
        scores=scores,
        raw_metrics=raw_metrics,
        positive_factors=list(report_payload["positive_factors"]),
        risk_factors=list(report_payload["risk_factors"]),
        competitor_stores=competitor_rows,
        report_payload=report_payload,
    )
    session.commit()
    return build_analysis_response(
        area_model,
        category_model,
        request.radius_m,
        result.id,
        normalize_raw_metrics(result.raw_metrics),
        scores,
        result.positive_factors,
        result.risk_factors,
        normalize_competitor_stores(result.competitor_stores),
        normalize_report_payload(result.report_payload),
    )


def get_saved_analysis(session: Session, analysis_id: str) -> AnalysisResponse:
    request, result = analysis_repository.get_analysis_result(session, analysis_id)
    area_model = catalog_repository.get_area(session, request.area_id)
    category_model = catalog_repository.get_category(session, request.category_id)
    scores = {
        "overall_fit_score": result.overall_fit_score,
        "competition_score": result.competition_score,
        "demand_score": result.demand_score,
        "land_use_score": result.land_use_score,
        "churn_risk_score": result.churn_risk_score,
    }
    return build_analysis_response(
        area_model,
        category_model,
        request.radius_m,
        result.id,
        normalize_raw_metrics(result.raw_metrics),
        scores,
        result.positive_factors,
        result.risk_factors,
        normalize_competitor_stores(result.competitor_stores),
        normalize_report_payload(result.report_payload),
    )


def build_analysis_response(
    area_model,
    category_model,
    radius_m: int,
    analysis_id: str,
    raw_metrics: RawMetrics,
    scores: dict[str, int],
    positive_factors: list[str],
    risk_factors: list[str],
    competitor_stores: list[CompetitorStorePayload],
    report_payload: ReportPayloadData,
) -> AnalysisResponse:
    return AnalysisResponse(
        analysis_id=analysis_id,
        area=AreaSummary(
            id=area_model.id,
            name=area_model.name,
            district_name=area_model.district_name,
            administrative_dong_name=area_model.administrative_dong_name,
            is_mock=area_model.is_mock,
        ),
        category=CategorySummary(
            id=category_model.id,
            code=category_model.code,
            name=category_model.name,
            group_name=category_model.group_name,
            similarity_group=category_model.similarity_group,
        ),
        radius_m=radius_m,
        scores=ScoreBreakdown(**scores),
        raw_metrics=raw_metrics,
        positive_factors=positive_factors,
        risk_factors=risk_factors,
        competitor_stores=[CompetitorStoreItem(**item) for item in competitor_stores],
        report_payload=ReportPayloadResponse(**report_payload),
    )
