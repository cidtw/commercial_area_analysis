import type { AnalysisResponse } from "@/lib/types";

import { ScoreInsightCard } from "./score-insight-card";

type MetricGridProps = {
  analysis: AnalysisResponse;
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

function clampValue(value: number) {
  if (value < 0) {
    return 0;
  }
  if (value > 100) {
    return 100;
  }
  return Math.round(value);
}

function buildScoreInsights(analysis: AnalysisResponse) {
  const same500m = numberValue(analysis.raw_metrics.same_category_count_500m);
  const similar500m = numberValue(analysis.raw_metrics.similar_category_count_500m);
  const closeRate = numberValue(analysis.raw_metrics.close_rate_12m) * 100;
  const demandScore = analysis.scores.demand_score;
  const locationScore = analysis.scores.land_use_score;
  const stabilityScore = analysis.scores.stability_score;
  const competitionLevel = clampValue(same500m * 22 + similar500m * 11);
  const riskLevel = clampValue(closeRate * 2);

  return [
    {
      title: "경쟁 강도",
      value: competitionLevel,
      tone: competitionLevel >= 65 ? "amber" : "green",
      summary:
        competitionLevel >= 65 ? "경쟁은 높은 편이에요" : "경쟁은 아주 과열된 수준은 아니에요",
      evidence: `반경 500m 안 동종 ${same500m}곳, 유사 업종 ${similar500m}곳`
    },
    {
      title: "수요 가능성",
      value: demandScore,
      tone: demandScore >= 60 ? "blue" : "amber",
      summary: demandScore >= 60 ? "기본 수요는 비교적 확인돼요" : "수요는 추가 확인이 필요해요",
      evidence: `일평균 유동 ${numberValue(analysis.raw_metrics.foot_traffic_daily_average_index).toFixed(1)} · 주말 유동 ${numberValue(analysis.raw_metrics.foot_traffic_weekend_average_index).toFixed(1)}`
    },
    {
      title: "폐업 리스크",
      value: riskLevel,
      tone: riskLevel >= 60 ? "amber" : "green",
      summary: riskLevel >= 60 ? "운영 리스크가 높게 잡혀요" : "폐업 리스크는 아주 크지 않아요",
      evidence: `최근 12개월 폐업률 ${(closeRate || 0).toFixed(1)}%`
    },
    {
      title: "입지 적합성",
      value: locationScore,
      tone: locationScore >= 70 ? "green" : "blue",
      summary:
        locationScore >= 70 ? "입지 조건은 업종과 비교적 잘 맞아요" : "입지 해석은 추가 확인이 필요해요",
      evidence: `용도지역 ${String(analysis.raw_metrics.land_use_zone_name ?? "정보 없음")}`
    },
    {
      title: "상권 안정성",
      value: stabilityScore,
      tone: stabilityScore >= 60 ? "blue" : "amber",
      summary: stabilityScore >= 60 ? "상권 변화는 비교적 안정적이에요" : "상권 변동성을 보수적으로 봐야 해요",
      evidence: `평균 영업 기간 ${numberValue(analysis.raw_metrics.avg_operation_months).toFixed(1)}개월`
    }
  ] as const;
}

export function MetricGrid({ analysis }: MetricGridProps) {
  const scoreInsights = buildScoreInsights(analysis);

  return (
    <section className="scoreInsightSection">
      <div className="sectionIntro">
        <h2>왜 이런 결과가 나왔을까요?</h2>
        <p>핵심 지표를 한 번에 비교할 수 있게, 의미 중심으로 다시 정리했습니다.</p>
      </div>
      <div className="scoreInsightGrid">
        {scoreInsights.map((item) => (
          <ScoreInsightCard
            evidence={item.evidence}
            key={item.title}
            summary={item.summary}
            title={item.title}
            tone={item.tone}
            value={item.value}
          />
        ))}
      </div>
    </section>
  );
}
