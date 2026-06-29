const verdictLabels: Record<string, string> = {
  recommended: "추천",
  conditional: "조건부 추천",
  caution: "주의",
  not_recommended: "비추천"
};

type VerdictBadgeProps = {
  level: string;
};

export function VerdictBadge({ level }: VerdictBadgeProps) {
  const label = verdictLabels[level] ?? level;
  return <span className={`verdictBadge verdictBadge--${level}`}>{label}</span>;
}
