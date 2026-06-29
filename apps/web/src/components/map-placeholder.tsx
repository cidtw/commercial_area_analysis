import type { AnalysisResponse } from "@/lib/types";

import { MapEvidencePanel } from "./map-evidence-panel";

type MapPlaceholderProps = {
  analysis: AnalysisResponse;
};

export function MapPlaceholder({ analysis }: MapPlaceholderProps) {
  return <MapEvidencePanel analysis={analysis} />;
}
