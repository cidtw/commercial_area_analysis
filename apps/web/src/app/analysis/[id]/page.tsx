import type { Metadata } from "next";

import { AnalysisResultView } from "@/components/analysis-result-view";
import { getAnalysis } from "@/lib/analysis";

export async function generateMetadata({
  params
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;

  try {
    const analysis = await getAnalysis(id);
    return {
      title: `${analysis.area.name} · ${analysis.category.name} 분석 결과`,
      description: `${analysis.radius_m}m 반경 기준 상권 적합도와 경쟁 지표를 확인합니다.`
    };
  } catch {
    return {
      title: "분석 결과",
      description: "선택한 조건의 상권 분석 결과를 확인합니다."
    };
  }
}

export default async function AnalysisResultPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const analysis = await getAnalysis(id);

  return (
    <AnalysisResultView
      analysis={analysis}
      description={`${analysis.radius_m}m 반경으로 계산된 mock sample data 기반 결과입니다.`}
      eyebrow="Analysis Result"
    />
  );
}
