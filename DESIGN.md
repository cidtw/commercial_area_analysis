# Commercial Area Analysis MVP Design System

## 1. Atmosphere & Identity

도시 탐색을 위한 조용한 소비자용 리포트. 화려한 부동산 광고나 SaaS 대시보드가 아니라, 사용자가 결과를 먼저 이해하고 필요할 때만 근거를 펼쳐보는 보고서처럼 느껴져야 한다. 시그니처는 "calm decision report"로, 여백과 타이포그래피로 정보 위계를 만들고 카드 사용은 절제한다.

## 2. Color

### Palette

| Role | Token | Light | Dark | Usage |
|------|-------|-------|------|-------|
| Surface/primary | --surface-primary | #f4f6fa | #111418 | App background |
| Surface/secondary | --surface-secondary | #edf2f8 | #182028 | Secondary panels |
| Surface/elevated | --surface-elevated | #ffffff | #22303b | Cards, modal blocks |
| Text/primary | --text-primary | #191f28 | #eef3f6 | Headline, body |
| Text/secondary | --text-secondary | #4e5968 | #adc0cc | Supporting text |
| Text/tertiary | --text-tertiary | #8b95a1 | #81939f | Captions |
| Border/default | --border-default | #dbe2ea | #2f3f4c | Default borders |
| Border/subtle | --border-subtle | #edf1f5 | #24313b | Light dividers |
| Accent/primary | --accent-primary | #3182f6 | #64b3cf | CTAs, focus |
| Accent/hover | --accent-hover | #1f6fe5 | #89d0e8 | Hover state |
| Status/success | --status-success | #2f9e5b | #59c083 | Positive indicators |
| Status/warning | --status-warning | #e28b2d | #e7a14d | Cautions |
| Status/error | --status-error | #d35f3f | #ec7c71 | Risks, errors |
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

- Primary: `"Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif`
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

### Result Hero

- **Structure**: title / 한 줄 요약 / 보조 설명 / CTA / verdict summary
- **Variants**: desktop split, mobile single flow
- **Spacing**: `--space-5`, `--space-6`, `--space-8`
- **Accessibility**: h1 + button labels + clear reading order

### Score Insight Card

- **Structure**: 지표명 / 점수 / 짧은 해석 / meter / raw metric 한 줄
- **Variants**: blue, amber, green
- **Spacing**: `--space-4`, `--space-5`
- **Accessibility**: 지표명과 해석을 함께 읽을 수 있어야 함

### Evidence Accordion

- **Structure**: section intro / details-summary blocks
- **Variants**: competition, demand, operations, source limits
- **Spacing**: `--space-4`, `--space-5`
- **Accessibility**: native details/summary 사용

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
