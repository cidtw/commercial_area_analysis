import { ScoreMeter } from "./score-meter";

type ScoreInsightCardProps = {
  title: string;
  value: number;
  summary: string;
  evidence: string;
  tone?: "blue" | "amber" | "green";
};

export function ScoreInsightCard({
  title,
  value,
  summary,
  evidence,
  tone = "blue"
}: ScoreInsightCardProps) {
  return (
    <article className="scoreInsightCard">
      <div className="scoreInsightHeader">
        <h3>{title}</h3>
        <strong>{value}점</strong>
      </div>
      <p className="scoreInsightSummary">{summary}</p>
      <ScoreMeter tone={tone} value={value} />
      <p className="scoreInsightEvidence">{evidence}</p>
    </article>
  );
}
