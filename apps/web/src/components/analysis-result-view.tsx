import Link from "next/link";

import type { AnalysisResponse } from "@/lib/types";

import { CompetitorList } from "./competitor-list";
import { MapPlaceholder } from "./map-placeholder";
import { MetricGrid } from "./metric-grid";
import { MockDataBadge } from "./mock-data-badge";
import { ReportPanel } from "./report-panel";
import { ScoreCard } from "./score-card";

type AnalysisResultViewProps = {
  analysis: AnalysisResponse;
  eyebrow: string;
  title?: string;
  description: string;
  showSampleGuide?: boolean;
};

export function AnalysisResultView({
  analysis,
  eyebrow,
  title,
  description,
  showSampleGuide = false
}: AnalysisResultViewProps) {
  return (
    <main className="pageShell">
      <section className="panel resultHero">
        <div className="panelHeader">
          <p className="eyebrow">{eyebrow}</p>
          <h1>
            {title ?? (
              <>
                {analysis.area.name} · {analysis.category.name}
              </>
            )}
          </h1>
          <p>{description}</p>
        </div>
        <MockDataBadge />
        {showSampleGuide ? (
          <div className="sampleGuide">
            <div>
              <strong>기본 샘플 조건</strong>
              <p>
                성수1가1동 · 카페 · 500m 반경 조합으로 즉시 렌더링한 예시입니다.
              </p>
            </div>
            <div className="sampleGuideActions">
              <Link className="primaryButton" href="/analysis">
                다른 조건으로 분석
              </Link>
              <Link className="secondaryButton" href="/methodology">
                산식과 데이터 보기
              </Link>
            </div>
          </div>
        ) : null}
        <div className="scoreRow">
          <ScoreCard label="종합 적합도" score={analysis.scores.overall_fit_score} tone="positive" />
          <ScoreCard label="경쟁 강도" score={analysis.scores.competition_score} />
          <ScoreCard label="수요 점수" score={analysis.scores.demand_score} />
          <ScoreCard label="용도 적합성" score={analysis.scores.land_use_score} />
          <ScoreCard label="개폐업 리스크" score={analysis.scores.churn_risk_score} tone="warning" />
        </div>
      </section>
      <MetricGrid metrics={analysis.raw_metrics} />
      <div className="resultGrid">
        <MapPlaceholder analysis={analysis} />
        <ReportPanel analysis={analysis} />
      </div>
      <CompetitorList stores={analysis.competitor_stores} />
    </main>
  );
}
