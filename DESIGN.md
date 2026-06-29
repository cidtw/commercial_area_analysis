# Commercial Area Analysis MVP Design System

## 1. Atmosphere & Identity

도시 탐색을 위한 조용한 분석 데스크. 화려한 부동산 광고가 아니라, 데이터를 차분하게 읽고 판단 근거를 남기는 도구처럼 느껴져야 한다. 시그니처는 "layered field notes"로, 패널과 카드가 지도 위 조사 노트처럼 정리되되 과장된 색상과 과잉 모션 없이 명확한 정보 대비를 유지한다.

## 2. Color

### Palette

| Role | Token | Light | Dark | Usage |
|------|-------|-------|------|-------|
| Surface/primary | --surface-primary | #f5f2ea | #111418 | App background |
| Surface/secondary | --surface-secondary | #ece6d7 | #182028 | Secondary panels |
| Surface/elevated | --surface-elevated | #fffdf7 | #22303b | Cards, modal blocks |
| Text/primary | --text-primary | #16212b | #eef3f6 | Headline, body |
| Text/secondary | --text-secondary | #556472 | #adc0cc | Supporting text |
| Text/tertiary | --text-tertiary | #7c8b97 | #81939f | Captions |
| Border/default | --border-default | #d6cdbb | #2f3f4c | Default borders |
| Border/subtle | --border-subtle | #e5ddce | #24313b | Light dividers |
| Accent/primary | --accent-primary | #0d5a75 | #64b3cf | CTAs, focus |
| Accent/hover | --accent-hover | #0b4a60 | #89d0e8 | Hover state |
| Status/success | --status-success | #2f7d54 | #59c083 | Positive indicators |
| Status/warning | --status-warning | #b76a17 | #e7a14d | Cautions |
| Status/error | --status-error | #b44538 | #ec7c71 | Risks, errors |
| Status/info | --status-info | #315c8b | #77a9e0 | Informational indicators |

### Rules

- 배경은 종이 질감에 가까운 중립 색을 사용하고, 인터랙션에는 청록 계열 accent만 쓴다.
- 위험/성공 상태 색은 데이터 카드와 배지에만 사용한다.
- 새 색이 필요하면 먼저 이 문서를 확장한다.

## 3. Typography

### Scale

| Level | Size | Weight | Line Height | Tracking | Usage |
|-------|------|--------|-------------|----------|-------|
| Display | 52px / 3.25rem | 700 | 1.04 | -0.03em | Landing hero |
| H1 | 38px / 2.375rem | 700 | 1.1 | -0.02em | Page titles |
| H2 | 30px / 1.875rem | 600 | 1.2 | -0.015em | Section titles |
| H3 | 22px / 1.375rem | 600 | 1.35 | -0.01em | Card titles |
| Body/lg | 18px / 1.125rem | 400 | 1.6 | 0 | Lead copy |
| Body | 16px / 1rem | 400 | 1.6 | 0 | Default body |
| Body/sm | 14px / 0.875rem | 500 | 1.5 | 0 | Labels |
| Caption | 12px / 0.75rem | 600 | 1.4 | 0.04em | Metadata |
| Overline | 11px / 0.6875rem | 700 | 1.3 | 0.08em | Upper labels |

### Font Stack

- Primary: `"IBM Plex Sans KR", "Pretendard Variable", "Apple SD Gothic Neo", sans-serif`
- Mono: `"IBM Plex Mono", "JetBrains Mono", monospace`

### Rules

- 한 프로젝트에서 폰트 패밀리는 2개만 사용한다.
- 숫자와 코드성 지표는 mono를 사용해 정렬감을 준다.
- 본문은 14px 아래로 내리지 않는다.

## 4. Spacing & Layout

### Base Unit

모든 간격은 4px 단위를 기반으로 한다.

| Token | Value | Usage |
|-------|-------|-------|
| --space-1 | 4px | tight |
| --space-2 | 8px | compact |
| --space-3 | 12px | form padding |
| --space-4 | 16px | default spacing |
| --space-5 | 20px | card inner spacing |
| --space-6 | 24px | section inner spacing |
| --space-8 | 32px | block gap |
| --space-10 | 40px | section gap |
| --space-12 | 48px | large split |
| --space-16 | 64px | page rhythm |
| --space-20 | 80px | hero spacing |

### Grid

- Max content width: 1280px
- Column system: 12-column, 24px gutter
- Breakpoints: sm 640px, md 768px, lg 1024px, xl 1280px

### Rules

- 레이아웃은 왼쪽 정렬을 기본으로 하고, 지표 카드는 asymmetric grid를 허용한다.
- `min-h-[100dvh]`를 전체 화면 섹션 기본값으로 본다.

## 5. Components

### Metric Card

- **Structure**: title / numeric value / helper text / evidence note
- **Variants**: neutral, positive, caution, risk
- **Spacing**: `--space-5`, `--space-6`
- **States**: default, hover, focus-visible
- **Accessibility**: semantic heading, visible focus ring
- **Motion**: 180ms translate/opacity rise

### Filter Panel

- **Structure**: section label / select controls / submit button
- **Variants**: inline desktop, stacked mobile
- **Spacing**: `--space-4`, `--space-5`
- **States**: default, focus, disabled, submitting
- **Accessibility**: label + describedby
- **Motion**: none beyond focus/submit state

## 6. Motion & Interaction

### Timing

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 120ms | ease-out | Hover, press |
| Standard | 220ms | ease-in-out | Card reveal, tab switch |
| Emphasis | 420ms | cubic-bezier(0.16, 1, 0.3, 1) | Hero and result intro |

### Rules

- `transform`와 `opacity`만 애니메이션한다.
- 입력 요소는 hover, focus-visible, disabled를 모두 갖는다.
- `prefers-reduced-motion`에서 강조 모션을 끈다.

## 7. Depth & Surface

### Strategy

tonal-shift

서페이스는 밝기 차와 얇은 선으로만 분리한다. 무거운 그림자는 쓰지 않고, 필요할 때만 한 단계 진한 패널을 배치한다.

