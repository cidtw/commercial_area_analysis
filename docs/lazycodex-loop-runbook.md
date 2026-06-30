# LazyCodex Loop Runbook

## 목적

`docs/project-workflow.md`를 사람이 읽는 기준 문서로 두고, LazyCodex는 `.omo/plans/workflow-schedule-buildout.md`를 실행 계획으로 사용한다. 기본 원칙은 `오늘 = day-01`부터 시작해 하루에 하루치만 수행하는 것이다.

## 기본 실행 명령

프로젝트 루트:

```powershell
cd C:\Users\SGAEM\Desktop\agy\commercial_area_analysis
```

계획 실행:

```text
$start-work .omo/plans/workflow-schedule-buildout.md
```

## LazyCodex 호출 프롬프트

```text
목표 / 범위 / 읽을 파일 / 건드리지 말 것 / 검증 / 출력 제한

목표:
- docs/project-workflow.md와 .omo/plans/workflow-schedule-buildout.md를 기준으로 오늘 날짜에 해당하는 day만 진행하라.
- 주제는 이미 확정되었으니 재선정하지 말고, 선행 prerequisite가 남아 있으면 먼저 닫아라.

범위:
- commercial_area_analysis 내부에서 현재 day 체크박스와 그 검증만 수행.
- 완료된 day 체크박스는 반복하지 말고 다음 미완료 체크박스로 넘어가라.

읽을 파일:
- docs/project-workflow.md
- .omo/plans/workflow-schedule-buildout.md
- docs/lazycodex-loop-runbook.md
- 관련 구현 파일과 기존 문서

건드리지 말 것:
- 현재 날짜보다 뒤인 day
- 주제 재선정
- 비밀값, .env 실제 값, 외부 배포 설정
- unrelated 파일과 다른 하위 프로젝트

검증:
- 각 체크박스마다 가장 싼 의미 있는 검증 1개 이상 수행
- UI면 가능한 범위에서 실제 표면 확인
- blocker면 BLOCKED: 이유 / 필요한 입력 / 다음 추천 행동 형식으로 보고

출력 제한:
- 변경 파일
- 완료한 체크박스
- 실행한 검증
- 남은 체크박스
- residual risk
```

## 12일 빌드업 기준

- day-01: scope freeze
- day-02: architecture flow draft
- day-03: API/프론트 contract inventory
- day-04: data mode/source metadata rule
- day-05: location search UX draft
- day-06: result report information architecture
- day-07: minimum demo scenario
- day-08: failure-state matrix
- day-09: UI polish backlog
- day-10: presentation architecture/storyline
- day-11: pre-demo checklist
- day-12: final run sheet

## 날짜 기반 실행 규칙

- 오늘은 `day-01`로 시작한다.
- 이후에는 하루 한 번 재호출할 때 다음 day로 진행한다.
- 이전 day 미완료가 있으면 다음 day로 넘어가지 않는다.
- 미래 day는 기본적으로 금지한다.

## day-01 완료 기준

- `docs/day-01-scope-freeze.md`가 존재한다.
- 아래 4개 섹션이 모두 채워져 있다.
  - 분석 대상 권역
  - 핵심 업종군
  - source metadata 범위
  - 용어 정리
- day-02가 참조할 고정 용어와 범위가 더 이상 미정 상태가 아니다.

## day-02 진입 조건

- day-01 완료 기준 충족
- blocker 없음
- `workflow-schedule-buildout.md`의 day-01 관련 checkbox가 닫힘

## 반복 호출 규칙

- 하루 한 번 또는 작업 세션 시작 시 같은 프롬프트로 재호출
- LazyCodex는 `.omo/plans/workflow-schedule-buildout.md`의 첫 미완료 체크박스부터 이어서 진행
- 같은 day 안의 잔여 작업을 우선 소진

## BLOCKED 보고 형식

```text
BLOCKED:
- reason:
- evidence:
- user input needed:
- recommended next step:
```

## fast-forward가 필요할 때

```text
추가 지시: 현재 날짜와 무관하게 다음 day까지 fast-forward 허용. 단, 각 day 완료 보고를 분리하라.
```
