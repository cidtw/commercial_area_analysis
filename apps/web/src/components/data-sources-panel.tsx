import type { AnalysisResponse } from "@/lib/types";

import { DataSourceNotice } from "./data-source-notice";

type DataSourcesPanelProps = {
  analysis: AnalysisResponse;
};

export function DataSourcesPanel({ analysis }: DataSourcesPanelProps) {
  return <DataSourceNotice analysis={analysis} />;
}
