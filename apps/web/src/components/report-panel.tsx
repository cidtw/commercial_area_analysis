import type { AnalysisResponse } from "@/lib/types";

type ReportPanelProps = {
  analysis: AnalysisResponse;
};

export function ReportPanel({ analysis }: ReportPanelProps) {
  return (
    <section className="panel reportPanel">
      <div className="panelHeader">
        <p className="eyebrow">AI Report</p>
        <h3>계산 지표 기반 요약</h3>
      </div>
      <p className="reportSummary">{analysis.report_payload.summary}</p>
      <div className="factorColumns">
        <div>
          <h4>긍정 요소</h4>
          <ul>
            {analysis.positive_factors.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>위험 요소</h4>
          <ul>
            {analysis.risk_factors.length > 0 ? (
              analysis.risk_factors.map((item) => <li key={item}>{item}</li>)
            ) : (
              <li>현재 지표 기준으로 즉시 강조할 위험 문구는 없습니다.</li>
            )}
          </ul>
        </div>
      </div>
      <div className="disclaimerBox">
        {analysis.report_payload.disclaimers.map((item) => (
          <p key={item}>{item}</p>
        ))}
      </div>
    </section>
  );
}

