type ScoreMeterProps = {
  value: number;
  tone?: "blue" | "amber" | "green";
};

function clampValue(value: number) {
  if (value < 0) {
    return 0;
  }
  if (value > 100) {
    return 100;
  }
  return value;
}

export function ScoreMeter({ value, tone = "blue" }: ScoreMeterProps) {
  const safeValue = clampValue(value);

  return (
    <div aria-hidden className={`scoreMeter scoreMeter--${tone}`}>
      <div className="scoreMeterFill" style={{ width: `${safeValue}%` }} />
    </div>
  );
}
