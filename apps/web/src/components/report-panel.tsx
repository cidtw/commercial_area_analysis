import type { AnalysisResponse } from "@/lib/types";

import { PrimaryReasonList } from "./primary-reason-list";

type ReportPanelProps = {
  analysis: AnalysisResponse;
};

export function ReportPanel({ analysis }: ReportPanelProps) {
  return (
    <PrimaryReasonList items={[...analysis.recommendation_reasons, ...analysis.warning_reasons].slice(0, 3)} />
  );
}
