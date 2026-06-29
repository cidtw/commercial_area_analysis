import type { AnalysisResponse } from "@/lib/types";

type MapEvidencePanelProps = {
  analysis: AnalysisResponse;
};

export function MapEvidencePanel({ analysis }: MapEvidencePanelProps) {
  return (
    <section className="mapEvidencePanel">
      <div className="sectionIntro">
        <h2>지도에서 근거 보기</h2>
        <p>수치만 보지 않고, 반경과 경쟁 업소 위치를 눈으로 확인할 수 있게 정리했습니다.</p>
      </div>

      <div className="mapEvidenceFrame">
        <div className="mapEvidenceCircle">
          <div className="mapEvidencePin" />
        </div>
        <div className="mapEvidenceSummary">
          <strong>{analysis.area.name}</strong>
          <p>{analysis.radius_m}m 반경, 경쟁 업소와 행정동 경계 기준</p>
        </div>
      </div>

      <div className="mapLegendList">
        {analysis.map_layers.map((layer) => (
          <div className="mapLegendItem" key={layer.layer_id}>
            <span>{layer.label}</span>
            <small>{layer.feature_collection.features.length}개 표시</small>
          </div>
        ))}
      </div>
    </section>
  );
}
