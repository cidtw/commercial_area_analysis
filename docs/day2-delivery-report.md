# Day 2 Delivery Report

## Status

2026-07-01 기준 day2 루프는 ULW 세션 `day2-es-toolkit-ui-20260701`에서 `complete`로 마감됐다.

이번 보고서는 두 묶음을 함께 정리한다.

1. day2 루프에서 완료한 결과 리포트 재설계
2. 그 직후 코드 리뷰를 반영하며 정리한 API 안정화/버그 픽스

## Day 2 Loop Deliverables

### 1. Result report redesign complete

- `/sample`와 `/analysis/[id]` 결과 화면을 단일 소비자 리포트 흐름으로 재구성했다.
- 화면 순서를 `verdict -> reasons -> score insight -> map evidence -> disclosure -> source notice`로 고정했다.
- 영어/대시보드 톤 라벨을 한국어 소비자 문장으로 교체했다.
- `result-presentation.ts`로 recommendation/data-mode/score/evidence 표현 로직을 통합했다.

### 2. Design system and repo-local skill added

- `DESIGN.md`에 `resultReport`, `verdictHero`, `scoreMeter`, `evidenceDisclosure`, `sourceNotice` primitive를 문서화했다.
- `toss/es-toolkit`의 source-first, small-surface, no-extra-dependency 원칙을 로컬 스킬 `.agents/skills/es-toolkit-result-guidance/SKILL.md`로 정리했다.

### 3. Browser-backed QA evidence captured

- mock API를 분리해 `/sample` 결과 표면을 실제 렌더링까지 검증했다.
- HTTP 200, 텍스트 캡처, 전체 페이지 스크린샷을 `.omo/evidence/day2-es-toolkit-ui-*`로 남겼다.

## Post-review API Fixes

### 1. Kakao geo fallback behavior fixed

- `KakaoLocalAdapter`가 REST key가 없을 때도 proxy fallback 경로를 사용할 수 있게 정리했다.
- direct Kakao 호출 실패 시 warning만 남기고 proxy 또는 internal catalog fallback으로 이어지게 만들었다.
- provider payload parsing을 좁혀 type-safe 하게 바꿨다.

### 2. Runtime dependency mismatch fixed

- app runtime 코드가 `httpx`를 사용하고 있었지만 runtime dependency에는 없던 상태를 수정했다.
- `apps/api/pyproject.toml`와 `apps/api/uv.lock`에서 `httpx`를 runtime dependency로 옮겼다.

### 3. Geo/catalog/ingest robustness tightened

- boundary 좌표 추출이 `Polygon`과 `MultiPolygon`을 모두 다루도록 보강됐다.
- coordinate resolution은 bounding-box candidate filtering 후 point-in-polygon, 마지막에 nearest fallback 순으로 정리됐다.
- store ingest는 `BATCH_SIZE` 기준 중간 commit이 가능하도록 바뀌었다.

## Verification

### Frontend

- `pnpm --filter commercial-area-analysis-web build`
  - pass
- mock API + Next runtime으로 `/sample` 검증
  - HTTP 200
  - text capture saved
  - screenshot saved

### API

- `uv run pytest tests/adapters/test_kakao_local.py tests/api/test_geo_endpoints.py tests/repositories/test_catalog.py tests/test_phase3_ingest.py`
  - `16 passed`
- `uv run ruff check ...`
  - pass
- `uv run basedpyright ...`
  - `0 errors`

### Known warning

- FastAPI `TestClient` 경로에서 `httpx` deprecation warning 1건이 남아 있다.
- 이번 버그 픽스 범위 밖이며, 추후 `httpx2` 전환 작업으로 분리하는 편이 맞다.

## Key Artifacts

- Loop summary image: `docs/assets/day2-loop-summary.svg`
- Delivery report image: `docs/assets/day2-delivery-report-summary.svg`
- Loop QA evidence:
  - `.omo/evidence/day2-es-toolkit-ui-build.log`
  - `.omo/evidence/day2-es-toolkit-ui-happy-head.txt`
  - `.omo/evidence/day2-es-toolkit-ui-happy.txt`
  - `.omo/evidence/day2-es-toolkit-ui-happy.png`
- API review verification:
  - pytest 16 passed
  - ruff pass
  - basedpyright 0 errors

## Commit Scope

이번 푸시에는 아래 범위가 포함된다.

- day2 result report redesign 관련 web/frontend 변경
- repo-local es-toolkit guidance skill
- day2 보고서 및 요약 이미지
- 리뷰 후 정리된 API fallback / ingest / boundary / dependency 픽스
