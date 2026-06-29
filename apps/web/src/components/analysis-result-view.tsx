import Link from "next/link";

import type { AnalysisResponse } from "@/lib/types";

import { CompetitorList } from "./competitor-list";
import { DataSourcesPanel } from "./data-sources-panel";
import { EvidenceAccordion } from "./evidence-accordion";
import { MapPlaceholder } from "./map-placeholder";
import { MetricGrid } from "./metric-grid";
import { ReportPanel } from "./report-panel";
import { VerdictBadge } from "./verdict-badge";

type AnalysisResultViewProps = {
  analysis: AnalysisResponse;
  eyebrow: string;
  title?: string;
  description: string;
  showSampleGuide?: boolean;
};

function numberValue(value: string | number | undefined) {
  if (typeof value === "number") {
    return value;
  }
  if (typeof value === "string") {
    return Number(value);
  }
  return 0;
}

function buildHeroDescription(analysis: AnalysisResponse) {
  const demandScore = analysis.scores.demand_score;
  const competitionCount = numberValue(analysis.raw_metrics.same_category_count_500m);
  const closeRate = numberValue(analysis.raw_metrics.close_rate_12m) * 100;

  const demandText =
    demandScore >= 70
      ? "수요는 비교적 충분하지만"
      : demandScore >= 45
        ? "수요는 어느 정도 있지만"
        : "수요는 아직 보수적으로 봐야 하고";

  const competitionText =
    competitionCount >= 4
      ? "주변 경쟁이 높은 편이에요."
      : competitionCount >= 2
        ? "경쟁 상황을 함께 점검해야 해요."
        : "주변 경쟁은 아주 높지는 않아요.";

  if (closeRate >= 25) {
    return `${analysis.radius_m}m 반경 기준, ${demandText} 최근 폐업 흐름과 경쟁 상황을 함께 봐야 해요.`;
  }

  return `${analysis.radius_m}m 반경 기준, ${demandText} ${competitionText}`;
}

function buildReasonItems(analysis: AnalysisResponse) {
  return [...analysis.recommendation_reasons, ...analysis.warning_reasons].slice(0, 3);
}

function buildResultTitle(analysis: AnalysisResponse, title?: string) {
  if (title) {
    return title;
  }
  return `${analysis.area.name} ${analysis.category.name} 입지 분석 결과`;
}

export function AnalysisResultView({
  analysis,
  eyebrow,
  title,
  description,
  showSampleGuide = false
}: AnalysisResultViewProps) {
  const heroDescription = buildHeroDescription(analysis);
  const titleText = buildResultTitle(analysis, title);

  return (
    <main className="consumerReportPage">
      <section className="consumerReportShell">
        <div className="resultHeroSection">
          <div className="resultHeroText">
            <p className="sectionEyebrow">{eyebrow}</p>
            <h1>{titleText}</h1>
            <p className="resultHeroLead">{heroDescription}</p>
            <p className="resultHeroSubcopy">{description}</p>
            <div className="heroButtonRow">
              <Link className="primaryButton" href="/analysis">
                다른 조건으로 다시 분석
              </Link>
              <Link className="secondaryButton" href="#details">
                근거 자세히 보기
              </Link>
            </div>
          </div>

          <aside className="resultVerdictPanel">
            <div className="resultVerdictHeader">
              <span>이번 분석 결과</span>
              <VerdictBadge level={analysis.recommendation_level} />
            </div>
            <strong className="resultVerdictScore">{analysis.scores.overall_fit_score}점</strong>
            <p className="resultVerdictSummary">{analysis.report_payload.summary}</p>
            {showSampleGuide ? (
              <p className="sampleInlineNotice">샘플 데이터 기준으로 바로 확인할 수 있는 예시 화면입니다.</p>
            ) : null}
          </aside>
        </div>

        <ReportPanel analysis={analysis} />

        <MetricGrid analysis={analysis} />

        <section className="mapEvidenceSection">
          <MapPlaceholder analysis={analysis} />
          <CompetitorList stores={analysis.competitor_stores} />
        </section>

        <EvidenceAccordion analysis={analysis} />

        <DataSourcesPanel analysis={analysis} />
      </section>
    </main>
  );
}
