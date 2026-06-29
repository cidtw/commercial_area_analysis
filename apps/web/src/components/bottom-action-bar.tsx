import Link from "next/link";

type BottomActionBarProps = {
  detailHref: string;
};

export function BottomActionBar({ detailHref }: BottomActionBarProps) {
  return (
    <div className="bottomActionBar">
      <Link className="secondaryButton" href={detailHref}>
        근거 자세히 보기
      </Link>
      <Link className="primaryButton" href="/analysis">
        다른 조건으로 다시 분석
      </Link>
    </div>
  );
}
