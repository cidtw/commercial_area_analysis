from typing import TypedDict

MetricValue = float | int | str
RawMetrics = dict[str, MetricValue]


class CompetitorStorePayload(TypedDict):
    id: str
    name: str
    category_name: str
    distance_m: float
    address: str
    status: str
    is_mock: bool
    latitude: float
    longitude: float


class SelectedLocationPayload(TypedDict):
    latitude: float
    longitude: float
    label: str
    source: str
    address: str | None
    region: str | None


class LlmReadyPayload(TypedDict):
    area_name: str
    category_name: str
    radius_m: int
    scores: dict[str, int]
    raw_metrics: RawMetrics
    positive_factors: list[str]
    risk_factors: list[str]
    instructions: list[str]


class ReportPayloadData(TypedDict):
    summary: str
    positive_factors: list[str]
    risk_factors: list[str]
    metric_evidence: RawMetrics
    disclaimers: list[str]
    llm_ready_payload: LlmReadyPayload
