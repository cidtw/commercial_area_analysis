import type { AnalysisResponse } from "@/lib/types";

type EvidenceAccordionProps = {
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

export function EvidenceAccordion({ analysis }: EvidenceAccordionProps) {
  const same500m = numberValue(analysis.raw_metrics.same_category_count_500m);
  const similar500m = numberValue(analysis.raw_metrics.similar_category_count_500m);
  const dailyTraffic = numberValue(analysis.raw_metrics.foot_traffic_daily_average_index);
  const weekendTraffic = numberValue(analysis.raw_metrics.foot_traffic_weekend_average_index);
  const closeRate = numberValue(analysis.raw_metrics.close_rate_12m);
  const operationMonths = numberValue(analysis.raw_metrics.avg_operation_months);
  const zoneName = String(analysis.raw_metrics.land_use_zone_name ?? "정보 없음");
  const zoneFitness = String(analysis.raw_metrics.land_use_fitness ?? "정보 없음");

  return (
    <section className="evidenceAccordion" id="details">
      <div className="sectionIntro">
        <h2>세부 근거</h2>
        <p>처음에는 핵심만 보고, 필요할 때만 세부 지표를 펼쳐 확인할 수 있게 정리했습니다.</p>
      </div>

      <details className="evidenceItem">
        <summary>경쟁 환경 자세히 보기</summary>
        <div className="evidenceBody">
          <p>
            500m 안에는 동종 업소 {same500m}곳, 유사 업종 {similar500m}곳이 잡혀 있습니다.
          </p>
          <p>가까운 경쟁 업소 목록과 지도 marker를 함께 보면서 실제 체감 경쟁을 확인하세요.</p>
        </div>
      </details>

      <details className="evidenceItem">
        <summary>수요 지표 자세히 보기</summary>
        <div className="evidenceBody">
          <p>
            일평균 유동 지수는 {dailyTraffic.toFixed(1)}, 주말 유동 지수는 {weekendTraffic.toFixed(1)}
            입니다.
          </p>
          <p>유동이 높더라도 실제 고객층과 시간대가 맞는지는 지도와 현장 조사로 함께 확인해야 합니다.</p>
        </div>
      </details>

      <details className="evidenceItem">
        <summary>운영 안정성 자세히 보기</summary>
        <div className="evidenceBody">
          <p>
            최근 12개월 폐업률은 {(closeRate * 100).toFixed(1)}%이고, 평균 영업 기간은{" "}
            {operationMonths.toFixed(1)}개월입니다.
          </p>
          <p>리스크 해석은 절대값보다 주변 상권 변화와 함께 보수적으로 읽는 편이 안전합니다.</p>
        </div>
      </details>

      <details className="evidenceItem">
        <summary>데이터 출처와 한계</summary>
        <div className="evidenceBody">
          <p>
            용도지역은 {zoneName}, 적합성 해석은 {zoneFitness}로 계산됐습니다.
          </p>
          <p>
            이번 화면은 샘플 데이터 기반 테스트 결과이며, 실제 창업 판단에는 최신 상권 데이터와 임대료,
            현장 확인이 함께 필요합니다.
          </p>
        </div>
      </details>
    </section>
  );
}
