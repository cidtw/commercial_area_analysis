import { apiBaseUrl } from "@/lib/config";
import type { AnalysisResponse } from "@/lib/types";

export const sampleAnalysisRequest = {
  area_id: "area-seongsu-1",
  category_id: "cat-cafe",
  radius_m: 500
} as const;

export async function getAnalysis(analysisId: string): Promise<AnalysisResponse> {
  const response = await fetch(`${apiBaseUrl}/api/analysis/${analysisId}`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("analysis not found");
  }
  return (await response.json()) as AnalysisResponse;
}

export async function createSampleAnalysis(): Promise<AnalysisResponse> {
  const response = await fetch(`${apiBaseUrl}/api/analysis`, {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sampleAnalysisRequest)
  });

  if (!response.ok) {
    throw new Error("sample analysis creation failed");
  }

  return (await response.json()) as AnalysisResponse;
}
