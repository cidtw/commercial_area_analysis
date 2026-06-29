export type AreaSummary = {
  id: string;
  name: string;
  district_name: string;
  administrative_dong_name: string;
  is_mock: boolean;
};

export type CategorySummary = {
  id: string;
  code: string;
  name: string;
  group_name: string;
  similarity_group: string;
};

export type ScoreBreakdown = {
  overall_fit_score: number;
  competition_score: number;
  demand_score: number;
  land_use_score: number;
  churn_risk_score: number;
  stability_score: number;
  accessibility_score: number;
};

export type CompetitorStore = {
  id: string;
  name: string;
  category_name: string;
  distance_m: number;
  address: string;
  status: string;
  is_mock: boolean;
  latitude: number;
  longitude: number;
};

export type DatasetSource = {
  source_key: string;
  source_name: string;
  source_version: string;
  reference_date: string;
  license_note: string;
  data_mode: string;
};

export type SelectedLocation = {
  latitude: number;
  longitude: number;
  label: string;
  source: string;
  address?: string | null;
  region?: string | null;
};

export type ResolvedRegion = {
  area_id?: string | null;
  area_name: string;
  district_name: string;
  administrative_dong_name: string;
};

export type DataCoverage = {
  status: "ready" | "insufficient";
  message: string;
};

export type GeoLayer = {
  layer_id: string;
  label: string;
  data_mode: string;
  feature_collection: {
    type: string;
    features: Array<Record<string, unknown>>;
  };
};

export type ReportPayload = {
  summary: string;
  positive_factors: string[];
  risk_factors: string[];
  metric_evidence: Record<string, string | number>;
  disclaimers: string[];
  llm_ready_payload: Record<string, unknown>;
};

export type AnalysisResponse = {
  analysis_id: string;
  area: AreaSummary;
  category: CategorySummary;
  radius_m: number;
  data_mode: string;
  methodology_version: string;
  scores: ScoreBreakdown;
  raw_metrics: Record<string, string | number>;
  positive_factors: string[];
  risk_factors: string[];
  competitor_stores: CompetitorStore[];
  data_sources: DatasetSource[];
  recommendation_level: string;
  recommendation_reasons: string[];
  warning_reasons: string[];
  selected_location?: SelectedLocation | null;
  resolved_region?: ResolvedRegion | null;
  nearby_competitors: CompetitorStore[];
  unavailable_data_warnings: string[];
  data_coverage: DataCoverage;
  map_layers: GeoLayer[];
  report_payload: ReportPayload;
};

export type GeoSearchItem = {
  label: string;
  source: string;
  latitude: number;
  longitude: number;
  address?: string | null;
  region?: string | null;
};

export type GeoSearchResponse = {
  query: string;
  type: "address" | "place" | "region";
  items: GeoSearchItem[];
};

export type GeoReverseResponse = {
  label: string;
  source: string;
  latitude: number;
  longitude: number;
  address?: string | null;
  region?: string | null;
};

export type DataSourceListResponse = {
  items: DatasetSource[];
};

export type MethodologyResponse = {
  version: string;
  data_modes: string[];
  disclaimer: string;
  score_formulae: Array<{
    score_key: string;
    title: string;
    formula: string;
    inputs: string[];
  }>;
};
