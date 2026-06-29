type MetricGridProps = {
  metrics: Record<string, string | number>;
};

const metricLabels: Record<string, string> = {
  same_category_count_300m: "동종 업소 300m",
  same_category_count_500m: "동종 업소 500m",
  same_category_count_1000m: "동종 업소 1km",
  similar_category_count_500m: "유사 업종 500m",
  competition_density_index: "경쟁 밀도",
  foot_traffic_daily_average_index: "일평균 유동",
  foot_traffic_weekend_average_index: "주말 유동",
  close_rate_12m: "12개월 폐업률",
  survival_rate_12m: "12개월 생존율",
  land_use_zone_name: "용도지역",
  land_use_fitness: "용도 적합성"
};

export function MetricGrid({ metrics }: MetricGridProps) {
  return (
    <div className="metricGrid">
      {Object.entries(metrics)
        .filter(([key]) => key in metricLabels)
        .map(([key, value]) => (
          <article className="metricCard" key={key}>
            <p className="metricLabel">{metricLabels[key]}</p>
            <p className="metricValue">{String(value)}</p>
          </article>
        ))}
    </div>
  );
}

