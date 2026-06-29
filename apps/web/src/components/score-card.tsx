type ScoreCardProps = {
  label: string;
  score: number;
  tone?: "default" | "positive" | "warning";
};

export function ScoreCard({ label, score, tone = "default" }: ScoreCardProps) {
  return (
    <article className={`scoreCard scoreCard--${tone}`}>
      <p className="eyebrow">{label}</p>
      <div className="scoreValue">{score}</div>
    </article>
  );
}

