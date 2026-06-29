type PrimaryReasonListProps = {
  items: string[];
};

export function PrimaryReasonList({ items }: PrimaryReasonListProps) {
  return (
    <section className="primaryReasonList">
      <div className="sectionLabel">핵심 이유</div>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
