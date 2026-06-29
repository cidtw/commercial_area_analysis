import type { Metadata } from "next";

import { MockDataBadge } from "@/components/mock-data-badge";
import { getDataSources, getMethodology } from "@/lib/analysis";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "데이터와 방법론",
  description: "상권분석 MVP의 source provenance, 점수 산식, 면책 기준을 설명합니다."
};

export default async function MethodologyPage() {
  const [methodology, dataSources] = await Promise.all([getMethodology(), getDataSources()]);

  return (
    <main className="pageShell">
      <section className="panel">
        <div className="panelHeader">
          <p className="eyebrow">데이터와 방법</p>
          <h1>사용 데이터, 산식, 면책 문구</h1>
          <p>
            현재 버전은 서울 성수권 mock/sample subset 구조를 기준으로 동작하며, 실제 창업 성공이나
            매출을 보장하지 않습니다.
          </p>
        </div>
        <div className="badgeRow">
          {methodology.data_modes.map((mode) => (
            <MockDataBadge key={mode} mode={mode} />
          ))}
        </div>
        <div className="methodologyGrid">
          <article className="metricCard">
            <h3>방법론 버전</h3>
            <p>{methodology.version}</p>
            <small>{methodology.disclaimer}</small>
          </article>
          <article className="metricCard">
            <h3>사용 데이터</h3>
            <div className="sourceList">
              {dataSources.items.map((source) => (
                <div className="sourceRow" key={`${source.source_key}-${source.reference_date}`}>
                  <div>
                    <strong>{source.source_name}</strong>
                    <p>
                      {source.source_version} · {source.reference_date}
                    </p>
                  </div>
                  <span>{source.data_mode}</span>
                </div>
              ))}
            </div>
          </article>
        </div>
        <div className="formulaGrid">
          {methodology.score_formulae.map((formula) => (
            <article className="metricCard" key={formula.score_key}>
              <p className="metricLabel">{formula.score_key}</p>
              <h3>{formula.title}</h3>
              <p>{formula.formula}</p>
              <small>{formula.inputs.join(", ")}</small>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
