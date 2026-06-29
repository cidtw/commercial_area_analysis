from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.catalog import list_areas, list_categories
from app.schemas.analysis import AnalysisRequestBody, AnalysisResponse, ReportPayloadResponse
from app.schemas.catalog import AreaListResponse, AreaSummary, CategoryListResponse, CategorySummary
from app.services.analysis_service import get_saved_analysis, run_analysis

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
    )


@router.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, session: Session = Depends(get_db_session)) -> AnalysisResponse:
    return get_saved_analysis(session, analysis_id)


@router.get("/api/analysis/{analysis_id}/report", response_model=ReportPayloadResponse)
def get_analysis_report(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> ReportPayloadResponse:
    return get_saved_analysis(session, analysis_id).report_payload
