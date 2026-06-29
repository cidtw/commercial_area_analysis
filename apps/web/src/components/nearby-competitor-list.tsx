import type { CompetitorStore } from "@/lib/types";

type NearbyCompetitorListProps = {
  stores: CompetitorStore[];
};

export function NearbyCompetitorList({ stores }: NearbyCompetitorListProps) {
  const visibleStores = stores.slice(0, 5);

  return (
    <section className="nearbyCompetitorList">
      <div className="sectionIntro">
        <h2>가까운 경쟁 업소</h2>
        <p>지도와 함께 보면, 실제 경쟁 강도를 더 직관적으로 이해할 수 있습니다.</p>
      </div>

      <div className="nearbyCompetitorItems">
        {visibleStores.length > 0 ? (
          visibleStores.map((store) => (
            <article className="nearbyCompetitorItem" key={store.id}>
              <div>
                <strong>{store.name}</strong>
                <p>
                  {store.category_name} · {store.address}
                </p>
              </div>
              <span>{store.distance_m.toFixed(0)}m</span>
            </article>
          ))
        ) : (
          <article className="nearbyCompetitorItem nearbyCompetitorItem--empty">
            <p>현재 반경 기준으로 표시할 경쟁 업소가 없습니다.</p>
          </article>
        )}
      </div>
    </section>
  );
}
