import type { AnalysisResponse } from "@/lib/types";

type MapPlaceholderProps = {
  analysis: AnalysisResponse;
};

export function MapPlaceholder({ analysis }: MapPlaceholderProps) {
  return (
    <section className="panel mapPanel">
      <div className="panelHeader">
        <p className="eyebrow">Map Placeholder</p>
        <h3>지도 연동 준비 구역</h3>
      </div>
      <div className="mapFrame">
        <div className="mapMarker" />
        <p>{analysis.area.name}</p>
        <small>{analysis.radius_m}m 반경 기준 경쟁 업소와 용도지역 데이터를 표시할 자리입니다.</small>
      </div>
    </section>
  );
}

