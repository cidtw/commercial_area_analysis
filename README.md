# Commercial Area Analysis MVP

서울 일부 행정동 샘플을 대상으로 소상공인/예비창업자가 지역과 업종을 선택하면 상권 지표와 설명형 리포트를 확인할 수 있는 MVP입니다.

## Workspace

```text
apps/api   FastAPI backend
apps/web   Next.js frontend
docs/      methodology and data notes
scripts/   seed and helper scripts
plans/     user-facing implementation plans
```

## Principles

- LLM은 계산된 지표를 설명할 뿐, 상권 사실을 생성하지 않습니다.
- 데이터 적재, 공간 계산, 점수화, 리포트 생성, UI를 분리합니다.
- 초기 범위는 서울 성동구 성수권 mock sample data입니다.
- 비밀 값과 외부 API key는 저장소에 넣지 않습니다.

## Quick Start

```bash
pnpm dev
```

- 웹: `http://127.0.0.1:3000`
- 샘플 화면: `http://127.0.0.1:3000/sample`
- 분석 폼: `http://127.0.0.1:3000/analysis`
