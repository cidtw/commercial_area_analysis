import type { Metadata } from "next";

import { AnalysisForm } from "./ui/analysis-form";

export const metadata: Metadata = {
  title: "분석 조건 선택",
  description: "지역, 업종, 반경을 선택해 상권 적합도 분석을 실행합니다."
};

export default function AnalysisPage() {
  return (
    <main className="pageShell">
      <section className="panel">
        <div className="panelHeader">
          <p className="eyebrow">Analysis Form</p>
          <h1>분석 조건 선택</h1>
          <p>
            현재는 성동구 성수권 샘플 지역만 제공합니다. 결과는 참고용이며, 실제 입지 판단 전에
            현장 확인이 필요합니다.
          </p>
        </div>
        <AnalysisForm />
      </section>
    </main>
  );
}
