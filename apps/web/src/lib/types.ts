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
};

export type CompetitorStore = {
  id: string;
  name: string;
  category_name: string;
  distance_m: number;
  address: string;
  status: string;
  is_mock: boolean;
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
  scores: ScoreBreakdown;
  raw_metrics: Record<string, string | number>;
  positive_factors: string[];
  risk_factors: string[];
  competitor_stores: CompetitorStore[];
  report_payload: ReportPayload;
};

