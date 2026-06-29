from collections.abc import Mapping
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.catalog import AreaSummary, CategorySummary


class AnalysisLocationInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    label: str
    source: str
    address: str | None = None
    region: str | None = None


class AnalysisRequestBody(BaseModel):
    model_config = ConfigDict(frozen=True)

    area_id: str | None = None
    category_id: str
    radius_m: Literal[300, 500, 1000]
    data_mode: Literal["mock", "sample", "real"] = "mock"
    location: AnalysisLocationInput | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "AnalysisRequestBody":
        if self.area_id is None and self.location is None:
            raise ValueError("area_id or location is required")
        return self


class SelectedLocationResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    latitude: float
    longitude: float
    label: str
    source: str
    address: str | None = None
    region: str | None = None


class ResolvedRegionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    area_id: str | None = None
    area_name: str
    district_name: str
    administrative_dong_name: str


class DataCoverageResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ready", "insufficient"]
    message: str


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(frozen=True)

    overall_fit_score: int
    competition_score: int
    demand_score: int
    land_use_score: int
    churn_risk_score: int
    stability_score: int
    accessibility_score: int


class CompetitorStoreItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    category_name: str
    distance_m: float
    address: str
    status: str
    is_mock: bool
    latitude: float
    longitude: float


class DatasetSourceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_key: str
    source_name: str
    source_version: str
    reference_date: date
    license_note: str
    data_mode: str


class GeoLayerResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    layer_id: str
    label: str
    data_mode: str
    feature_collection: Mapping[str, object]


class AnalysisGeoResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    analysis_id: str
    data_mode: str
    layers: list[GeoLayerResponse]


class DataSourceListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[DatasetSourceItem]


class ScoreFormulaItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    score_key: str
    title: str
    formula: str
    inputs: list[str]


class MethodologyResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    data_modes: list[str]
    score_formulae: list[ScoreFormulaItem]
    disclaimer: str


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
    data_mode: str
    methodology_version: str
    scores: ScoreBreakdown
    raw_metrics: Mapping[str, float | int | str]
    positive_factors: list[str]
    risk_factors: list[str]
    competitor_stores: list[CompetitorStoreItem]
    data_sources: list[DatasetSourceItem]
    recommendation_level: str
    recommendation_reasons: list[str]
    warning_reasons: list[str]
    selected_location: SelectedLocationResponse | None = None
    resolved_region: ResolvedRegionResponse | None = None
    nearby_competitors: list[CompetitorStoreItem] = []
    unavailable_data_warnings: list[str] = []
    data_coverage: DataCoverageResponse
    map_layers: list[GeoLayerResponse]
    report_payload: ReportPayloadResponse
