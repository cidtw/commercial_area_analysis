import type { Metadata } from "next";

import { AnalysisResultView } from "@/components/analysis-result-view";
import { createSampleAnalysis } from "@/lib/analysis";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "샘플 분석 보기",
  description: "성수권 테스트 데이터로 즉시 확인할 수 있는 상권분석 데모 화면"
};

export default async function SamplePage() {
  const analysis = await createSampleAnalysis();

  return (
    <AnalysisResultView
      analysis={analysis}
      description="샘플 데이터로 동작하는 테스트 결과입니다. 실제 창업 판단 전에는 최신 데이터와 현장 확인이 함께 필요합니다."
      eyebrow="샘플 결과"
      showSampleGuide
    />
  );
}
