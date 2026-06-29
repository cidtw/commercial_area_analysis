const modeLabel: Record<string, string> = {
  mock: "샘플 데이터",
  sample: "부분 샘플 데이터",
  real: "실데이터"
};

type MockDataBadgeProps = {
  mode?: string;
};

export function MockDataBadge({ mode = "mock" }: MockDataBadgeProps) {
  return <span className={`mockBadge mockBadge--${mode}`}>{modeLabel[mode] ?? `${mode} data`}</span>;
}
