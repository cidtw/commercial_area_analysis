from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

from sqlalchemy.orm import Session

from app.adapters.sources.registry import build_phase2_sources
from app.analysis.geometry import build_circle_polygon
from app.analysis.methodology import (
    METHODLOGY_DATA_MODES,
    METHODOLOGY_DISCLAIMER,
    METHODOLOGY_VERSION,
    SCORE_FORMULAE,
)
from app.analysis.metrics import build_metric_snapshot
from app.analysis.recommendations import build_recommendation
from app.analysis.scoring import build_scores
from app.core.config import get_settings
from app.domain.payloads import (
    CompetitorStorePayload,
    RawMetrics,
    ReportPayloadData,
    SelectedLocationPayload,
)
from app.reporting.report_payload import build_report_payload
from app.repositories import analysis as analysis_repository
from app.repositories import catalog as catalog_repository
from app.schemas.analysis import (
    AnalysisGeoResponse,
    AnalysisLocationInput,
    AnalysisResponse,
    CompetitorStoreItem,
    DataCoverageResponse,
    DatasetSourceItem,
    DataSourceListResponse,
    GeoLayerResponse,
    MethodologyResponse,
    ReportPayloadResponse,
    ResolvedRegionResponse,
    ScoreBreakdown,
    ScoreFormulaItem,
    SelectedLocationResponse,
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
    items: list[CompetitorStorePayload] = []
    for item in payload:
        items.append(
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
                latitude=(
                    float(item["latitude"])
                    if isinstance(item["latitude"], (float, int, str))
                    else 0.0
                ),
                longitude=(
                    float(item["longitude"])
                    if isinstance(item["longitude"], (float, int, str))
                    else 0.0
                ),
            ),
        )
    return items


def normalize_data_source_items(
    payload: Sequence[Mapping[str, object]],
) -> list[DatasetSourceItem]:
    items: list[DatasetSourceItem] = []
    for item in payload:
        reference_value = item.get("reference_date", date(2026, 6, 1))
        if isinstance(reference_value, str):
            reference_date = date.fromisoformat(reference_value)
        elif isinstance(reference_value, date):
            reference_date = reference_value
        else:
            reference_date = date(2026, 6, 1)
        items.append(
            DatasetSourceItem(
                source_key=str(item["source_key"]),
                source_name=str(item["source_name"]),
                source_version=str(item["source_version"]),
                reference_date=reference_date,
                license_note=str(item["license_note"]),
                data_mode=str(item["data_mode"]),
            ),
        )
    return items


def normalize_geo_layers(payload: Sequence[Mapping[str, object]]) -> list[GeoLayerResponse]:
    return [
        GeoLayerResponse(
            layer_id=str(item["layer_id"]),
            label=str(item["label"]),
            data_mode=str(item["data_mode"]),
            feature_collection=normalize_mapping(item["feature_collection"]),
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
            normalize_mapping(payload.get("metric_evidence", {})),
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
                normalize_mapping(llm_ready_payload.get("raw_metrics", {})),
            ),
            "positive_factors": normalize_string_list(
                llm_ready_payload.get("positive_factors", []),
            ),
            "risk_factors": normalize_string_list(llm_ready_payload.get("risk_factors", [])),
            "instructions": normalize_string_list(
                llm_ready_payload.get("instructions", []),
            ),
        },
    )


def normalize_selected_location(value: object) -> SelectedLocationPayload | None:
    if not isinstance(value, Mapping):
        return None
    try:
        latitude = float(value["latitude"])
        longitude = float(value["longitude"])
        label = str(value["label"])
        source = str(value["source"])
    except (KeyError, TypeError, ValueError):
        return None
    return SelectedLocationPayload(
        latitude=latitude,
        longitude=longitude,
        label=label,
        source=source,
        address=str(value["address"]) if value.get("address") is not None else None,
        region=str(value["region"]) if value.get("region") is not None else None,
    )


def build_mock_data_source(data_label: str) -> dict[str, object]:
    return {
        "source_key": "mock_seed_source",
        "source_name": data_label,
        "source_version": "2026.06",
        "reference_date": "2026-06-01",
        "license_note": "local mock sample data for development and tests",
        "data_mode": "mock",
    }


def build_analysis_data_sources(
    data_label: str,
    *,
    data_mode: str,
    included_source_keys: Sequence[str],
) -> list[dict[str, object]]:
    if data_mode == "mock":
        return [build_mock_data_source(data_label)]

    items = [build_mock_data_source(data_label)]
    source_registry = build_phase2_sources()
    for key in included_source_keys:
        descriptor = source_registry[key].describe()
        items.append(
            {
                "source_key": descriptor.source_key,
                "source_name": descriptor.source_name,
                "source_version": descriptor.source_version,
                "reference_date": descriptor.reference_date.isoformat(),
                "license_note": descriptor.license_note,
                "data_mode": descriptor.data_mode,
            },
        )
    return items


def build_analysis_map_layers(
    *,
    area_model,
    competitor_rows: list[CompetitorStorePayload],
    radius_m: int,
    data_mode: str,
    selected_location: SelectedLocationPayload | None = None,
) -> list[dict[str, object]]:
    center_latitude = (
        selected_location["latitude"] if selected_location is not None else area_model.center_latitude
    )
    center_longitude = (
        selected_location["longitude"] if selected_location is not None else area_model.center_longitude
    )
    boundary_geometry = area_model.boundary_geojson or {
        "type": "Polygon",
        "coordinates": [
            build_circle_polygon(center_latitude, center_longitude, 40),
        ],
    }
    boundary_features = [
        {
            "type": "Feature",
            "properties": {
                "area_id": area_model.id,
                "area_name": area_model.name,
            },
            "geometry": boundary_geometry,
        },
    ]
    radius_features = [
        {
            "type": "Feature",
            "properties": {
                "radius_m": radius_m,
                "area_id": area_model.id,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    build_circle_polygon(
                        center_latitude,
                        center_longitude,
                        radius_m,
                    ),
                ],
            },
        },
    ]
    competitor_features = [
        {
            "type": "Feature",
            "properties": {
                "store_id": row["id"],
                "name": row["name"],
                "category_name": row["category_name"],
                "distance_m": row["distance_m"],
                "status": row["status"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]],
            },
        }
        for row in competitor_rows
    ]
    return [
        {
            "layer_id": "selected-location",
            "label": "선택 위치",
            "data_mode": data_mode,
            "feature_collection": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "label": (
                                selected_location["label"]
                                if selected_location is not None
                                else area_model.name
                            ),
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [center_longitude, center_latitude],
                        },
                    },
                ],
            },
        },
        {
            "layer_id": "selected-area-boundary",
            "label": "선택 행정동 경계",
            "data_mode": area_model.data_mode,
            "feature_collection": {"type": "FeatureCollection", "features": boundary_features},
        },
        {
            "layer_id": "analysis-radius",
            "label": "분석 반경",
            "data_mode": data_mode,
            "feature_collection": {"type": "FeatureCollection", "features": radius_features},
        },
        {
            "layer_id": "competitor-stores",
            "label": "경쟁 업소",
            "data_mode": data_mode,
            "feature_collection": {"type": "FeatureCollection", "features": competitor_features},
        },
    ]


def run_analysis(
    session: Session,
    *,
    area_id: str | None,
    category_id: str,
    radius_m: int,
    data_mode: str,
    location: AnalysisLocationInput | None = None,
) -> AnalysisResponse:
    settings = get_settings()
    selected_location = (
        SelectedLocationPayload(
            latitude=location.lat,
            longitude=location.lng,
            label=location.label,
            source=location.source,
            address=location.address,
            region=location.region,
        )
        if location is not None
        else None
    )
    if area_id is not None:
        area_model = catalog_repository.get_area(session, area_id)
    elif selected_location is not None:
        matched_area = catalog_repository.find_area_for_point(
            session,
            latitude=selected_location["latitude"],
            longitude=selected_location["longitude"],
        )
        if matched_area is None:
            raise LookupError("area not found for selected location")
        area_model = matched_area
    else:
        raise LookupError("area not found")
    category_model = catalog_repository.get_category(session, category_id)
    area = catalog_repository.to_area_record(area_model)
    category = catalog_repository.to_category_record(category_model)
    requested_data_mode = data_mode
    if selected_location is None:
        stores = catalog_repository.to_store_records(
            catalog_repository.get_stores_with_categories_for_analysis(
                session,
                area=area,
                radius_m=1000,
                data_mode=requested_data_mode,
            ),
        )
    else:
        stores = catalog_repository.to_store_records(
            catalog_repository.get_stores_with_categories_for_point(
                session,
                latitude=selected_location["latitude"],
                longitude=selected_location["longitude"],
                radius_m=1000,
                data_mode=requested_data_mode,
            ),
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
    competition = catalog_repository.to_district_competition_record(
        catalog_repository.get_district_competition_stat(session, area.id, category.id)
        if requested_data_mode == "sample"
        else None,
    )
    stability = catalog_repository.to_district_stability_record(
        catalog_repository.get_district_stability_stat(session, area.id, category.id)
        if requested_data_mode == "sample"
        else None,
    )
    sales = catalog_repository.to_district_sales_record(
        catalog_repository.get_district_sales_stat(session, area.id, category.id)
        if requested_data_mode == "sample"
        else None,
    )
    has_sample_data = requested_data_mode == "sample" and (
        bool(stores)
        or competition is not None
        or stability is not None
        or sales is not None
        or area_model.data_mode == "sample"
    )
    effective_data_mode = "sample" if has_sample_data else "mock"
    unavailable_data_warnings: list[str] = []
    coverage_status = "ready"
    coverage_message = "분석 가능한 데이터가 준비되어 있습니다."
    if requested_data_mode == "sample" and effective_data_mode == "mock":
        stores = catalog_repository.to_store_records(
            catalog_repository.get_stores_with_categories_for_analysis(
                session,
                area=area,
                radius_m=1000,
                data_mode="mock",
            ),
        )
        competition = None
        stability = None
        sales = None
        unavailable_data_warnings.append(
            "sample subset 데이터가 없어 mock sample data로 대체했습니다.",
        )
        coverage_status = "insufficient"
        coverage_message = "선택한 범위의 sample 데이터가 부족해 mock 기반으로 대체했습니다."
    if requested_data_mode == "real":
        effective_data_mode = "real"
        if not stores:
            unavailable_data_warnings.append(
                "선택한 반경 내에 import된 실제 업소 데이터가 부족합니다.",
            )
            coverage_status = "insufficient"
            coverage_message = "해당 위치의 실제 업소 데이터가 아직 충분하지 않습니다."

    center_latitude = (
        selected_location["latitude"] if selected_location is not None else area.center_latitude
    )
    center_longitude = (
        selected_location["longitude"] if selected_location is not None else area.center_longitude
    )

    raw_metrics, competitor_rows = build_metric_snapshot(
        area=area,
        category=category,
        stores=stores,
        traffic=foot_traffic,
        land_use_zones=land_use_zones,
        open_close=open_close,
        competition=competition,
        stability=stability,
        sales=sales,
        selected_radius_m=radius_m,
        center_latitude=center_latitude,
        center_longitude=center_longitude,
    )
    scores = build_scores(raw_metrics)
    recommendation_level, recommendation_reasons, warning_reasons = build_recommendation(
        scores=scores,
        raw_metrics=raw_metrics,
    )
    included_source_keys: list[str] = []
    if stores and effective_data_mode == "sample":
        included_source_keys.append("soba_store_source")
    if competition is not None:
        included_source_keys.append("seoul_competition_source")
    if stability is not None:
        included_source_keys.append("seoul_stability_source")
    if sales is not None:
        included_source_keys.append("seoul_sales_source")
    if area_model.data_mode == "sample":
        included_source_keys.append("boundary_source")
    data_sources = build_analysis_data_sources(
        settings.mock_data_label,
        data_mode=effective_data_mode,
        included_source_keys=included_source_keys,
    )
    map_layers = build_analysis_map_layers(
        area_model=area_model,
        competitor_rows=competitor_rows,
        radius_m=radius_m,
        data_mode=effective_data_mode,
        selected_location=selected_location,
    )
    report_payload = build_report_payload(
        area_name=area.name,
        category_name=category.name,
        radius_m=radius_m,
        raw_metrics=raw_metrics,
        scores=scores,
        data_label=(
            "sample subset + mock base data"
            if effective_data_mode == "sample"
            else settings.mock_data_label
        ),
    )
    request = analysis_repository.create_analysis_request(
        session,
        area_id=area.id,
        category_id=category.id,
        radius_m=radius_m,
        data_mode=effective_data_mode,
        selected_boundary_id=f"boundary-{area.code}",
        input_snapshot={
            "area_id": area.id,
            "category_id": category.id,
            "radius_m": radius_m,
            "data_mode": requested_data_mode,
            "effective_data_mode": effective_data_mode,
            "selected_location": dict(selected_location) if selected_location is not None else None,
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
        data_mode=effective_data_mode,
        data_sources=data_sources,
        recommendation_level=recommendation_level,
        recommendation_reasons=recommendation_reasons,
        warning_reasons=warning_reasons,
        map_layers=map_layers,
        methodology_version=METHODOLOGY_VERSION,
    )
    session.commit()
    return build_analysis_response(
        area_model=area_model,
        category_model=category_model,
        radius_m=request.radius_m,
        analysis_id=result.id,
        data_mode=result.data_mode,
        methodology_version=result.methodology_version,
        raw_metrics=normalize_raw_metrics(result.raw_metrics),
        scores=scores,
        positive_factors=result.positive_factors,
        risk_factors=result.risk_factors,
        competitor_stores=normalize_competitor_stores(result.competitor_stores),
        data_sources=normalize_data_source_items(result.data_sources),
        recommendation_level=result.recommendation_level,
        recommendation_reasons=normalize_string_list(result.recommendation_reasons),
        warning_reasons=normalize_string_list(result.warning_reasons),
        selected_location=selected_location,
        resolved_region=ResolvedRegionResponse(
            area_id=area_model.id,
            area_name=area_model.name,
            district_name=area_model.district_name,
            administrative_dong_name=area_model.administrative_dong_name,
        ),
        unavailable_data_warnings=unavailable_data_warnings,
        data_coverage=DataCoverageResponse(status=coverage_status, message=coverage_message),
        map_layers=normalize_geo_layers(result.map_layers),
        report_payload=normalize_report_payload(result.report_payload),
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
        "stability_score": result.stability_score,
        "accessibility_score": result.accessibility_score,
    }
    return build_analysis_response(
        area_model=area_model,
        category_model=category_model,
        radius_m=request.radius_m,
        analysis_id=result.id,
        data_mode=result.data_mode,
        methodology_version=result.methodology_version,
        raw_metrics=normalize_raw_metrics(result.raw_metrics),
        scores=scores,
        positive_factors=result.positive_factors,
        risk_factors=result.risk_factors,
        competitor_stores=normalize_competitor_stores(result.competitor_stores),
        data_sources=normalize_data_source_items(result.data_sources),
        recommendation_level=result.recommendation_level,
        recommendation_reasons=normalize_string_list(result.recommendation_reasons),
        warning_reasons=normalize_string_list(result.warning_reasons),
        selected_location=normalize_selected_location(request.input_snapshot.get("selected_location")),
        resolved_region=ResolvedRegionResponse(
            area_id=area_model.id,
            area_name=area_model.name,
            district_name=area_model.district_name,
            administrative_dong_name=area_model.administrative_dong_name,
        ),
        unavailable_data_warnings=[],
        data_coverage=DataCoverageResponse(
            status="ready" if result.data_mode != "real" or result.competitor_stores else "insufficient",
            message=(
                "분석 가능한 데이터가 준비되어 있습니다."
                if result.data_mode != "real" or result.competitor_stores
                else "해당 위치의 실제 업소 데이터가 아직 충분하지 않습니다."
            ),
        ),
        map_layers=normalize_geo_layers(result.map_layers),
        report_payload=normalize_report_payload(result.report_payload),
    )


def build_analysis_response(
    *,
    area_model,
    category_model,
    radius_m: int,
    analysis_id: str,
    data_mode: str,
    methodology_version: str,
    raw_metrics: RawMetrics,
    scores: dict[str, int],
    positive_factors: list[str],
    risk_factors: list[str],
    competitor_stores: list[CompetitorStorePayload],
    data_sources: list[DatasetSourceItem],
    recommendation_level: str,
    recommendation_reasons: list[str],
    warning_reasons: list[str],
    selected_location: SelectedLocationPayload | None,
    resolved_region: ResolvedRegionResponse,
    unavailable_data_warnings: list[str],
    data_coverage: DataCoverageResponse,
    map_layers: list[GeoLayerResponse],
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
        data_mode=data_mode,
        methodology_version=methodology_version,
        scores=ScoreBreakdown(**scores),
        raw_metrics=raw_metrics,
        positive_factors=positive_factors,
        risk_factors=risk_factors,
        competitor_stores=[CompetitorStoreItem(**item) for item in competitor_stores],
        data_sources=data_sources,
        recommendation_level=recommendation_level,
        recommendation_reasons=recommendation_reasons,
        warning_reasons=warning_reasons,
        selected_location=(
            SelectedLocationResponse(**selected_location) if selected_location is not None else None
        ),
        resolved_region=resolved_region,
        nearby_competitors=[CompetitorStoreItem(**item) for item in competitor_stores],
        unavailable_data_warnings=unavailable_data_warnings,
        data_coverage=data_coverage,
        map_layers=map_layers,
        report_payload=ReportPayloadResponse(**report_payload),
    )


def get_saved_analysis_geo(session: Session, analysis_id: str) -> AnalysisGeoResponse:
    response = get_saved_analysis(session, analysis_id)
    return AnalysisGeoResponse(
        analysis_id=response.analysis_id,
        data_mode=response.data_mode,
        layers=response.map_layers,
    )


def get_data_sources(settings_label: str) -> DataSourceListResponse:
    mock_item = build_mock_data_source(settings_label)
    sample_items = build_analysis_data_sources(
        settings_label,
        data_mode="sample",
        included_source_keys=[
            "soba_store_source",
            "seoul_competition_source",
            "seoul_stability_source",
            "seoul_sales_source",
            "boundary_source",
        ],
    )[1:]
    return DataSourceListResponse(items=normalize_data_source_items([mock_item, *sample_items]))


def get_methodology() -> MethodologyResponse:
    return MethodologyResponse(
        version=METHODOLOGY_VERSION,
        data_modes=list(METHODLOGY_DATA_MODES),
        score_formulae=[
            ScoreFormulaItem(
                score_key=str(item["score_key"]),
                title=str(item["title"]),
                formula=str(item["formula"]),
                inputs=normalize_string_list(item["inputs"]),
            )
            for item in SCORE_FORMULAE
        ],
        disclaimer=METHODOLOGY_DISCLAIMER,
    )
