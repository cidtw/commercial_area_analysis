# Commercial Area Analysis MVP

[![release](https://img.shields.io/badge/release-v0.1.0-0d5a75)](https://github.com/cidtw/commercial_area_analysis/tags)
[![backend](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![frontend](https://img.shields.io/badge/frontend-Next.js-111111)](https://nextjs.org/)
[![data](https://img.shields.io/badge/data-mock%20sample-f59e0b)](./apps/api/app/adapters/mock_data/areas.json)

서울 일부 행정동 샘플을 대상으로 소상공인/예비창업자가 지역과 업종을 선택하면 상권 지표와 설명형 리포트를 확인할 수 있는 MVP입니다.

- 범위: 서울 성동구 성수권 mock sample data 기반 MVP
- 백엔드: FastAPI + SQLAlchemy + PostGIS-ready schema
- 프론트엔드: Next.js App Router
- 핵심 데모: `/sample`에서 테스트 데이터 기반 결과 즉시 확인

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

## First Release

- 태그: `v0.1.0`
- 상태: MVP baseline
- 포함 사항: 샘플 분석 화면, 설명 가능한 점수화, mock sample data 자동 시드, FastAPI/Next.js 로컬 개발 환경
