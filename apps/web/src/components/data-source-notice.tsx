import Link from "next/link";

import type { AnalysisResponse } from "@/lib/types";

import { MockDataBadge } from "./mock-data-badge";

type DataSourceNoticeProps = {
  analysis: AnalysisResponse;
};

export function DataSourceNotice({ analysis }: DataSourceNoticeProps) {
  const dataModeLabel = analysis.data_mode === "sample" ? "샘플 데이터" : "테스트 데이터";

  return (
    <section className="dataSourceNotice">
      <div className="dataSourceNoticeHeader">
        <div>
          <div className="sectionLabel">데이터 출처</div>
          <h2>{dataModeLabel} 기반 안내</h2>
        </div>
        <MockDataBadge mode={analysis.data_mode} />
      </div>
      <p className="dataSourceNoticeText">
        이 결과는 {dataModeLabel} 기반의 테스트 분석입니다. 실제 창업 결정에는 최신 상권 데이터,
        임대료, 현장 조사, 전문가 검토가 함께 필요합니다.
      </p>
      <div className="dataSourceList">
        {analysis.data_sources.map((source) => (
          <div className="dataSourceLine" key={`${source.source_key}-${source.reference_date}`}>
            <span>{source.source_name}</span>
            <small>
              {source.reference_date} · {source.data_mode}
            </small>
          </div>
        ))}
      </div>
      <Link className="inlineTextLink" href="/methodology">
        데이터 산식과 한계 보기
      </Link>
    </section>
  );
}
