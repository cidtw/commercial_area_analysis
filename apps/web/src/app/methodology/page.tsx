import type { Metadata } from "next";

import { MockDataBadge } from "@/components/mock-data-badge";

export const metadata: Metadata = {
  title: "데이터와 방법론",
  description: "상권분석 MVP의 mock data, 점수 산식, 면책 기준을 설명합니다."
};

export default function MethodologyPage() {
  return (
    <main className="pageShell">
      <section className="panel">
        <div className="panelHeader">
          <p className="eyebrow">About Data & Methodology</p>
          <h1>사용 데이터, 산식, 면책 문구</h1>
          <p>현재 버전은 성수권 mock sample data 기반이며, 실제 창업 성공이나 매출을 보장하지 않습니다.</p>
        </div>
        <MockDataBadge />
        <div className="methodologyGrid">
          <article className="metricCard">
            <h3>사용 데이터</h3>
            <p>areas, business_categories, stores, foot_traffic, land_use, open_close_stats</p>
          </article>
          <article className="metricCard">
            <h3>점수 산식</h3>
            <p>competition, demand, land_use, churn_risk를 가중 평균해 overall_fit_score를 계산합니다.</p>
          </article>
          <article className="metricCard">
            <h3>면책</h3>
            <p>이 서비스는 참고용 분석 도구이며, 투자 조언이나 성공 보장을 제공하지 않습니다.</p>
          </article>
        </div>
      </section>
    </main>
  );
}
