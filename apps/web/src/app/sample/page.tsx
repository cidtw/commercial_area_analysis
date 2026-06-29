import type { Metadata } from "next";

import { AnalysisResultView } from "@/components/analysis-result-view";
import { createSampleAnalysis } from "@/lib/analysis";

export const metadata: Metadata = {
  title: "샘플 분석 보기",
  description: "성수권 mock sample data로 즉시 확인할 수 있는 상권분석 데모 화면"
};

export default async function SamplePage() {
  const analysis = await createSampleAnalysis();

  return (
    <AnalysisResultView
      analysis={analysis}
      description="테스트 데이터로 즉시 확인할 수 있는 샘플 결과 화면입니다. 실제 서비스 흐름과 같은 계산 결과를 사용합니다."
      eyebrow="Sample Experience"
      showSampleGuide
      title="테스트 데이터 샘플 결과"
    />
  );
}
