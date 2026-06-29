import { apiBaseUrl } from "@/lib/config";
import type {
  AnalysisResponse,
  DataSourceListResponse,
  MethodologyResponse
} from "@/lib/types";

export const sampleAnalysisRequest = {
  area_id: "area-seongsu-1",
  category_id: "cat-cafe",
  radius_m: 500,
  data_mode: "mock"
} as const;

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`request failed: ${url}`);
  }
  return (await response.json()) as T;
}

export async function getAnalysis(analysisId: string): Promise<AnalysisResponse> {
  return fetchJson<AnalysisResponse>(`${apiBaseUrl}/api/analysis/${analysisId}`, {
    cache: "no-store"
  });
}

export async function createSampleAnalysis(): Promise<AnalysisResponse> {
  return fetchJson<AnalysisResponse>(`${apiBaseUrl}/api/analysis`, {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sampleAnalysisRequest)
  });
}

export async function getMethodology(): Promise<MethodologyResponse> {
  return fetchJson<MethodologyResponse>(`${apiBaseUrl}/api/methodology`, {
    next: { revalidate: 3600 }
  });
}

export async function getDataSources(): Promise<DataSourceListResponse> {
  return fetchJson<DataSourceListResponse>(`${apiBaseUrl}/api/data-sources`, {
    next: { revalidate: 3600 }
  });
}
