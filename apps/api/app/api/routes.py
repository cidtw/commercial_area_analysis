from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.repositories.catalog import list_areas, list_categories
from app.schemas.analysis import (
    AnalysisGeoResponse,
    AnalysisRequestBody,
    AnalysisResponse,
    DataSourceListResponse,
    MethodologyResponse,
    ReportPayloadResponse,
)
from app.schemas.catalog import AreaListResponse, AreaSummary, CategoryListResponse, CategorySummary
from app.services.analysis_service import (
    get_data_sources,
    get_methodology,
    get_saved_analysis,
    get_saved_analysis_geo,
    run_analysis,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/areas", response_model=AreaListResponse)
def get_areas(session: Session = Depends(get_db_session)) -> AreaListResponse:
    items = [
        AreaSummary(
            id=area.id,
            name=area.name,
            district_name=area.district_name,
            administrative_dong_name=area.administrative_dong_name,
            is_mock=area.is_mock,
        )
        for area in list_areas(session)
    ]
    return AreaListResponse(items=items)


@router.get("/api/categories", response_model=CategoryListResponse)
def get_categories(session: Session = Depends(get_db_session)) -> CategoryListResponse:
    items = [
        CategorySummary(
            id=category.id,
            code=category.code,
            name=category.name,
            group_name=category.group_name,
            similarity_group=category.similarity_group,
        )
        for category in list_categories(session)
    ]
    return CategoryListResponse(items=items)


@router.post("/api/analysis", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(
    body: AnalysisRequestBody,
    session: Session = Depends(get_db_session),
) -> AnalysisResponse:
    return run_analysis(
        session,
        area_id=body.area_id,
        category_id=body.category_id,
        radius_m=body.radius_m,
        data_mode=body.data_mode,
    )


@router.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, session: Session = Depends(get_db_session)) -> AnalysisResponse:
    return get_saved_analysis(session, analysis_id)


@router.get("/api/analysis/{analysis_id}/geo", response_model=AnalysisGeoResponse)
def get_analysis_geo(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> AnalysisGeoResponse:
    return get_saved_analysis_geo(session, analysis_id)


@router.get("/api/analysis/{analysis_id}/report", response_model=ReportPayloadResponse)
def get_analysis_report(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> ReportPayloadResponse:
    return get_saved_analysis(session, analysis_id).report_payload


@router.get("/api/data-sources", response_model=DataSourceListResponse)
def data_sources() -> DataSourceListResponse:
    return get_data_sources(get_settings().mock_data_label)


@router.get("/api/methodology", response_model=MethodologyResponse)
def methodology() -> MethodologyResponse:
    return get_methodology()
