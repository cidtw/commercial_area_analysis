import type { Metadata } from "next";
import Link from "next/link";

import { MockDataBadge } from "@/components/mock-data-badge";

export const metadata: Metadata = {
  title: "상권분석 MVP",
  description: "서울 성수권 mock sample data 기반 상권 적합도 분석 서비스"
};

export default function HomePage() {
  return (
    <main className="pageShell">
      <section className="heroCard">
        <div className="heroCopy">
          <p className="eyebrow">Commercial Area Analysis MVP</p>
          <h1>지역과 업종을 고르면, 지표 기반으로 상권 적합도를 읽어줍니다.</h1>
          <p className="lead">
            이 MVP는 성수권 mock sample data만으로 작동합니다. LLM은 계산된 metric을 설명할 뿐,
            상권 사실을 새로 만들어내지 않습니다.
          </p>
          <div className="heroActions">
            <Link className="primaryButton" href="/sample">
              샘플 바로 보기
            </Link>
            <Link className="primaryButton" href="/analysis">
              분석 시작
            </Link>
            <Link className="secondaryButton" href="/methodology">
              데이터와 산식 보기
            </Link>
          </div>
        </div>
        <div className="heroAside">
          <MockDataBadge />
          <ul className="checkList">
            <li>경쟁도, 유동성, 용도지역, 개폐업 리스크 분리 계산</li>
            <li>raw metric과 score breakdown 동시 제공</li>
            <li>향후 공공데이터 adapter로 교체 가능한 구조</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
