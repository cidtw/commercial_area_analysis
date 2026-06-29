import type { CompetitorStore } from "@/lib/types";

type CompetitorListProps = {
  stores: CompetitorStore[];
};

export function CompetitorList({ stores }: CompetitorListProps) {
  return (
    <section className="panel">
      <div className="panelHeader">
        <p className="eyebrow">주변 경쟁 업소</p>
        <h3>선택 반경 안의 경쟁 환경</h3>
      </div>
      <div className="storeList">
        {stores.map((store) => (
          <article className="storeRow" key={store.id}>
            <div>
              <strong>{store.name}</strong>
              <p>
                {store.category_name} · {store.address}
              </p>
            </div>
            <span>{store.distance_m.toFixed(0)}m</span>
          </article>
        ))}
      </div>
    </section>
  );
}

