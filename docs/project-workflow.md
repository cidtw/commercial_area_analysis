# Commercial Area Analysis Workflow Reset

## 기준 문서

- 참조 일정: `C:\Users\SGAEM\Desktop\프로젝트 진행 일정.pdf`
- 재정비 날짜: 2026-06-30
- 대상 프로젝트: `commercial_area_analysis`

## 목적

PDF에서 제시한 팀 프로젝트 기본 흐름인 `데이터 수집 → 데이터 취합 및 분석 → 워크플로우 구현 → 시각화 및 가공`을 현재 상권분석 프로젝트 구조에 맞게 다시 고정한다. 목표는 기능 목록을 늘리는 것이 아니라, 지금 있는 코드와 앞으로의 작업 순서를 같은 언어로 설명하는 운영 기준을 만드는 것이다.

## 1. 데이터 수집

현재 책임:

- 외부 공공데이터, fixture CSV, mock payload를 `source_name`, `source_version`, `reference_date`, `data_mode`와 함께 관리한다.
- 기준 파일:
  - `apps/api/app/adapters/`
  - `data/raw/`
  - `docs/data-sources.md`
  - `docs/real-data-ingestion.md`

완료 기준:

- 어떤 화면의 숫자든 원천 데이터 출처와 기준일을 역으로 설명할 수 있어야 한다.
- `mock`, `sample`, `real` 모드가 혼동되지 않아야 한다.

## 2. 데이터 취합 및 분석

현재 책임:

- 좌표, 반경, 업종, 용도지역, 경쟁 업소 수, 개폐업 지표를 같은 분석 계약으로 정리한다.
- 점수 계산과 설명 문구 생성을 분리한다.
- 기준 파일:
  - `apps/api/app/services/`
  - `apps/api/app/analysis/`
  - `apps/api/app/schemas/`
  - `docs/methodology.md`

완료 기준:

- 프론트에 전달되는 `analysis response` 하나로 점수, 근거, 데이터 범위, 지도 레이어를 모두 설명할 수 있어야 한다.
- LLM이 붙더라도 계산된 값만 읽고 새로운 상권 사실을 만들지 않아야 한다.

## 3. 워크플로우 구현

현재 책임:

- 위치 검색, 좌표 확정, fallback 지역 선택, 반경/업종 선택, 분석 실행, 결과 조회를 하나의 사용자 흐름으로 연결한다.
- 지도 provider, 검색 endpoint, 분석 endpoint, 프론트 폼 상태를 느슨하게 결합한다.
- 기준 파일:
  - `apps/web/src/app/analysis/ui/analysis-form.tsx`
  - `apps/web/src/lib/analysis.ts`
  - `apps/web/src/lib/config.ts`
  - `docs/map-provider.md`

완료 기준:

- 사용자는 GIS 도구를 배우지 않아도 “위치 선택 → 조건 선택 → 분석 실행” 흐름을 이해할 수 있어야 한다.
- API 미연결, 검색 실패, 데이터 부족 상태가 각각 분리되어 보여야 한다.

## 4. 시각화 및 가공

현재 책임:

- 결과 화면을 수치 나열이 아니라 의사결정용 리포트처럼 정리한다.
- 지도 근거, 경쟁 업소, 데이터 커버리지, 한계 고지를 같은 화면에서 읽게 만든다.
- 기준 파일:
  - `apps/web/src/app/page.tsx`
  - `apps/web/src/components/analysis-result-view.tsx`
  - `apps/web/src/app/globals.css`
  - `DESIGN.md`

완료 기준:

- 첫 화면은 프로젝트의 분석 구조를 한눈에 전달해야 한다.
- 결과 화면은 “점수 확인 → 핵심 이유 → 지도 근거 → 데이터 범위” 순으로 읽혀야 한다.

## 7월 운영 체크포인트

### 7월 1일 ~ 7월 3일

- 분석 대상 권역, 핵심 업종군, source metadata 범위를 고정한다.
- 화면/문서/코드에서 쓰는 용어를 하나로 맞춘다.

### 7월 6일 ~ 7월 10일

- 아키텍처 흐름도와 핵심 API 연동 레이아웃을 완성한다.
- 위치 검색과 결과 리포트의 최소 데모를 실제로 시연 가능 상태로 만든다.

### 7월 14일 ~ 7월 23일

- 예외 처리, 데이터 부족 상태, UI/UX 다듬기를 집중적으로 정리한다.
- mock/sample/real 모드가 화면에서 자연스럽게 구분되도록 정리한다.

### 7월 24일

- 발표 시연은 `분석 입력 → 결과 리포트 → 데이터 한계 고지` 순으로 진행한다.

## 화면 기준 읽기 순서

1. 홈: 분석 구조와 현재 프로젝트 상태를 소개한다.
2. 분석 폼: 위치와 조건을 확정한다.
3. 결과 화면: 점수보다 근거를 먼저 이해하게 만든다.
4. 방법론/출처: 데이터 한계와 계산 기준을 문서로 보완한다.
