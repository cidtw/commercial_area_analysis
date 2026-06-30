# workflow-schedule-buildout - Work Plan

## TL;DR (For humans)
**What you'll get:** 오늘을 1일차로 잡고 12일 동안 개발 초안을 단계적으로 쌓아 올리는 실행 플랜과, LazyCodex가 매일 같은 규칙으로 이어서 돌 수 있는 호출 문서를 받습니다.

**Why this approach:** `project-workflow.md`의 4단계 흐름은 유지하되, 실제 작업은 하루 단위 체크박스로 쪼개야 LazyCodex가 오늘 할 일만 정확히 집어 실행할 수 있습니다.

**What it will NOT do:** 미래 날짜 작업을 기본으로 당겨서 실행하지 않습니다.
외부 스케줄러나 cron을 설치하지 않습니다.
주제 자체를 다시 정하지 않습니다.

**Effort:** Medium
**Risk:** Low - 일정/문서/초안 아티팩트 중심이며 제품 코드 직접 변경은 최소화
**Decisions to sanity-check:** 오늘을 1일차로 고정할지, 특정 날짜 이후 fast-forward를 허용할지

Your next move: 1일차 산출물을 확인하고, 이후부터는 runbook 프롬프트로 LazyCodex를 하루 단위로 재호출합니다. Full execution detail follows below.

---

> TL;DR (machine): 12-day buildout plan starting today; execute one day at a time with date-gated lazycodex loop rules and day-specific artifacts.

## Scope
### Must have
- 오늘을 포함한 12일 buildout 일정
- LazyCodex용 하루 단위 실행 규칙
- 1일차 실제 산출물과 이후 날짜별 목표/검증 정의

### Must NOT have (guardrails, anti-slop, scope boundaries)
- 주제 재선정 작업을 다시 열지 말 것
- 외부 자동화 인프라 설치나 민감정보 설정을 끼워 넣지 말 것
- 현재 날짜보다 뒤인 day를 기본 실행 범위에 포함하지 말 것

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: none + 문서/플랜 정합성 검증
- Evidence: .omo/evidence/task-<N>-workflow-schedule-buildout.<ext>

## Execution strategy
### Parallel execution waves
> Target 5-8 todos per wave. Fewer than 3 (except the final) means you under-split.
- Wave 1: 12일 일정과 날짜 게이트 정의
- Wave 2: 일별 산출물과 검증 정의
- Wave 3: runbook 및 1일차 실행/정합성 점검

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 | - | 2, 3 | - |
| 2 | 1 | 4, 5 | 3 |
| 3 | 1 | 5, 6 | 2 |
| 4 | 2 | 7 | 5 |
| 5 | 2, 3 | 7 | 4, 6 |
| 6 | 3 | 7 | 5 |
| 7 | 4, 5, 6 | F1-F4 | - |

## Todos
> Implementation + Test = ONE todo. Never separate.
- [x] 1. 12일 buildout의 날짜 기준과 상위 흐름을 고정한다
  What to do / Must NOT do: 오늘을 1일차로 잡고 12일 구간을 day-01부터 day-12까지 고정한다. `수집 → 취합 및 분석 → 워크플로우 구현 → 시각화 및 가공` 상위 흐름은 유지하되 day 단위로 다시 매핑한다. 주제를 다시 바꾸지 말 것.
  Parallelization: Wave 1 | Blocked by: - | Blocks: 2, 3
  References (executor has NO interview context - be exhaustive): docs/project-workflow.md, docs/methodology.md, docs/data-sources.md
  Acceptance criteria (agent-executable): `.omo/plans/workflow-schedule-buildout.md` 안에 `day-01`부터 `day-12`까지 정의와 상위 4단계 흐름 유지 규칙이 존재한다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "day-01|day-12|데이터 수집|데이터 취합 및 분석|워크플로우 구현|시각화 및 가공" .omo/plans/workflow-schedule-buildout.md`; failure - day 표기나 4단계 중 하나라도 누락 시 fail. Evidence .omo/evidence/task-1-workflow-schedule-buildout.txt
  Commit: N | docs(plan): define 12-day buildout calendar

- [x] 2. 오늘 날짜 기준 하루치만 수행하는 실행 규칙을 명시한다
  What to do / Must NOT do: LazyCodex가 오늘 날짜에 해당하는 day와 선행 prerequisite까지만 실행하고, 다음 day는 기본적으로 건드리지 않는 규칙을 plan과 runbook에 적는다. fast-forward를 기본값으로 두지 말 것.
  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 4, 5
  References (executor has NO interview context - be exhaustive): docs/project-workflow.md, .omo/plans/workflow-schedule-buildout.md
  Acceptance criteria (agent-executable): plan과 runbook에 `오늘 = day-N`, `다음 day 금지`, `fast-forward` 관련 규칙이 있다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "오늘|day-|fast-forward|다음 day" .omo/plans/workflow-schedule-buildout.md docs/lazycodex-loop-runbook.md`; failure - 날짜 게이트 규칙 부재 시 fail. Evidence .omo/evidence/task-2-workflow-schedule-buildout.txt
  Commit: N | docs(plan): add day-gated execution rule

- [x] 3. 12일 일정을 day별 deliverable과 verification으로 분해한다
  What to do / Must NOT do: 각 day에 산출물, 최소 검증, 다음 day 진입 조건을 적는다. 막연한 `다듬기`만 남기지 말 것.
  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 5, 6
  References (executor has NO interview context - be exhaustive): docs/project-workflow.md, plans/gis-indicator-ux-phase2.md, README.md
  Acceptance criteria (agent-executable): 각 day 아래에 deliverable, verification, exit criteria가 존재한다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "Deliverable|Verification|Exit criteria" .omo/plans/workflow-schedule-buildout.md`; failure - day 설명이 검증 없이 남아 있으면 fail. Evidence .omo/evidence/task-3-workflow-schedule-buildout.txt
  Commit: N | docs(plan): decompose 12 days into deliverables

- [x] 4. day-01 루프 산출물인 scope freeze 문서를 작성한다
  What to do / Must NOT do: 주제는 확정되었다는 전제에서 day-01 산출물로 분석 대상 권역, 핵심 업종군, source metadata 범위, 공통 용어를 고정하는 문서를 만든다. 주제 후보 비교표는 만들지 말 것.
  Parallelization: Wave 3 | Blocked by: 2 | Blocks: 7
  References (executor has NO interview context - be exhaustive): docs/project-workflow.md, docs/methodology.md, docs/data-sources.md
  Acceptance criteria (agent-executable): day-01 산출물 문서에 `분석 대상 권역`, `핵심 업종군`, `source metadata`, `용어 정리` 섹션이 모두 존재한다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "분석 대상 권역|핵심 업종군|source metadata|용어 정리" docs/day-01-scope-freeze.md`; failure - 4개 섹션 중 하나라도 누락 시 fail. Evidence .omo/evidence/task-4-workflow-schedule-buildout.txt
  Commit: N | docs(day1): write scope freeze artifact

- [x] 5. LazyCodex용 12일 runbook을 작성한다
  What to do / Must NOT do: `docs/lazycodex-loop-runbook.md`에 복붙 가능한 프롬프트, 실행 명령, 재호출 규칙, today/day-N 규칙, blocker 보고 형식을 적는다. 추상 설명만 쓰고 실제 호출문을 빼먹지 말 것.
  Parallelization: Wave 3 | Blocked by: 2, 3 | Blocks: 7
  References (executor has NO interview context - be exhaustive): .omo/plans/workflow-schedule-buildout.md, docs/project-workflow.md, start-work skill behavior
  Acceptance criteria (agent-executable): runbook에 `$start-work`, `목표 / 범위 / 읽을 파일 / 건드리지 말 것 / 검증 / 출력 제한`, `BLOCKED`, `fast-forward`가 존재한다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "\\$start-work|목표 / 범위 / 읽을 파일 / 건드리지 말 것 / 검증 / 출력 제한|BLOCKED|fast-forward" docs/lazycodex-loop-runbook.md`; failure - 복붙 실행문이나 blocker 형식 부재 시 fail. Evidence .omo/evidence/task-5-workflow-schedule-buildout.txt
  Commit: N | docs(runbook): add 12-day lazycodex loop prompt

- [x] 6. 1일차 완료 보고와 2일차 진입 조건을 문서화한다
  What to do / Must NOT do: day-01 문서와 runbook에 `오늘 완료 기준`, `내일 시작 조건`을 명시한다. vague한 `다음에 이어서` 표현만 남기지 말 것.
  Parallelization: Wave 3 | Blocked by: 3 | Blocks: 7
  References (executor has NO interview context - be exhaustive): .omo/plans/workflow-schedule-buildout.md, docs/day-01-scope-freeze.md, docs/lazycodex-loop-runbook.md
  Acceptance criteria (agent-executable): day-01 산출물과 runbook에 day-02 진입 조건이 있다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "day-02|진입 조건|완료 기준" docs/day-01-scope-freeze.md docs/lazycodex-loop-runbook.md`; failure - 2일차 진입 조건 누락 시 fail. Evidence .omo/evidence/task-6-workflow-schedule-buildout.txt
  Commit: N | docs(day1): define day-02 entry criteria

- [x] 7. workflow 문서와 실행 아티팩트의 용어를 일치시킨다
  What to do / Must NOT do: `수집`, `취합 및 분석`, `워크플로우 구현`, `시각화 및 가공` 용어와 day-01 산출물의 표현이 project-workflow, plan, runbook에서 어긋나지 않게 맞춘다. 새 표현을 임의로 늘리지 말 것.
  Parallelization: Wave 3 | Blocked by: 4, 5, 6 | Blocks: F1-F4
  References (executor has NO interview context - be exhaustive): docs/project-workflow.md, .omo/plans/workflow-schedule-buildout.md, docs/lazycodex-loop-runbook.md, docs/day-01-scope-freeze.md
  Acceptance criteria (agent-executable): 네 문서 모두 핵심 4단계 용어를 공유한다.
  QA scenarios (name the exact tool + invocation): happy - `rg -n "데이터 수집|데이터 취합 및 분석|워크플로우 구현|시각화 및 가공" docs/project-workflow.md .omo/plans/workflow-schedule-buildout.md docs/lazycodex-loop-runbook.md docs/day-01-scope-freeze.md`; failure - 용어 불일치 발견 시 fail. Evidence .omo/evidence/task-7-workflow-schedule-buildout.txt
  Commit: N | docs(sync): align 12-day loop terminology

## Day map
### day-01
Deliverable: 주제 고정 전제의 scope freeze 문서, 핵심 권역/업종/용어/metadata 범위 고정  
Verification: 문서 섹션 존재 여부 grep  
Exit criteria: day-02가 참조할 권역/업종/용어가 더 이상 미정 상태가 아님

### day-02
Deliverable: 시스템 아키텍처 흐름도 초안과 책임선 문서  
Verification: 흐름도/컴포넌트 목록 문서 존재  
Exit criteria: 입력 → 분석 → 결과 흐름의 소유 파일이 설명됨

### day-03
Deliverable: API/프론트 contract inventory  
Verification: endpoint, payload, screen mapping 표 존재  
Exit criteria: day-04 구현 우선순위를 정할 수 있음

### day-04
Deliverable: source metadata와 data mode 운영 규칙 초안  
Verification: mock/sample/real 규칙 문서화  
Exit criteria: 데이터 표현 규칙이 팀 문서와 일치

### day-05
Deliverable: 위치 검색/좌표 확정 UX 초안 문서  
Verification: 상태별 UX checklist 존재  
Exit criteria: 검색, empty, error, fallback 흐름이 명시됨

### day-06
Deliverable: 결과 리포트 정보 구조 초안  
Verification: 결과 읽기 순서와 섹션 구조 문서 존재  
Exit criteria: 점수보다 근거 우선 읽기 구조가 설명됨

### day-07
Deliverable: 최소 데모 시나리오 정의  
Verification: demo entry, action, expected output 문서 존재  
Exit criteria: 실제 시연 경로를 한 줄로 설명 가능

### day-08
Deliverable: 예외 처리/데이터 부족 상태 매트릭스  
Verification: failure state matrix 존재  
Exit criteria: 없는 데이터와 준비 중 상태가 구분됨

### day-09
Deliverable: UI polish backlog  
Verification: 우선순위와 시각 기준 문서 존재  
Exit criteria: 후반 polish 범위를 작게 실행 가능

### day-10
Deliverable: 발표용 architecture/storyline draft  
Verification: 발표 순서 1차본 존재  
Exit criteria: 5분 내 시연 동선 설명 가능

### day-11
Deliverable: 최종 점검 checklist  
Verification: pre-demo checklist 존재  
Exit criteria: 발표 직전 확인 항목 완비

### day-12
Deliverable: 최종 데모 run sheet  
Verification: start-to-finish run sheet 존재  
Exit criteria: 발표 당일 그대로 따라갈 수 있음

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit
- [ ] F2. Code quality review
- [ ] F3. Real manual QA
- [ ] F4. Scope fidelity

## Commit strategy
- 기본은 no-commit. 사용자가 요청할 때만 문서 아티팩트를 묶어 `docs(lazycodex): add 12-day workflow loop artifacts`로 커밋한다.

## Success criteria
- `project-workflow.md`를 기준으로 하는 12일 buildout plan이 존재한다.
- LazyCodex용 복붙 실행 프롬프트와 재호출 규칙이 문서화된다.
- 오늘을 포함한 1일차 산출물이 실제 문서로 남는다.
