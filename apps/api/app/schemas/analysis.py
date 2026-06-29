from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.catalog import AreaSummary, CategorySummary


class AnalysisRequestBody(BaseModel):
    model_config = ConfigDict(frozen=True)

    area_id: str
    category_id: str
    radius_m: Literal[300, 500, 1000]


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(frozen=True)

    overall_fit_score: int
    competition_score: int
    demand_score: int
    land_use_score: int
    churn_risk_score: int


class CompetitorStoreItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    category_name: str
    distance_m: float
    address: str
    status: str
    is_mock: bool


class ReportPayloadResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    summary: str
    positive_factors: list[str]
    risk_factors: list[str]
    metric_evidence: Mapping[str, float | int | str]
    disclaimers: list[str]
    llm_ready_payload: Mapping[str, object]


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    analysis_id: str
    area: AreaSummary
    category: CategorySummary
    radius_m: int
    scores: ScoreBreakdown
    raw_metrics: Mapping[str, float | int | str]
    positive_factors: list[str]
    risk_factors: list[str]
    competitor_stores: list[CompetitorStoreItem]
    report_payload: ReportPayloadResponse
